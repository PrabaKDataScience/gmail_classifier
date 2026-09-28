import { useState, useEffect } from 'react'
import './App.css'

const API_BASE = 'http://localhost:8000/api'

function App() {
  const [emails, setEmails] = useState([])
  const [status, setStatus] = useState(null)
  const [pullCount, setPullCount] = useState(5)
  const [stats, setStats] = useState({
    categorized: 0,
    inputTokens: 0,
    category_counts: {}
  })
  const [isProcessing, setIsProcessing] = useState(false)
  const [jobProgress, setJobProgress] = useState({ total: 0, completed: 0, startTime: null })
  const [newCat, setNewCat] = useState({ name: '', description: '' })
  const [eta, setEta] = useState(null)

  const refreshStats = async () => {
    try {
      const res = await fetch(`${API_BASE}/stats`)
      const data = await res.json()
      setStats(data.stats)
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    fetch(`${API_BASE}/status`)
      .then(res => res.json())
      .then(data => setStatus(data))
      .catch(err => console.error(err))
      
    refreshStats()
  }, [])

  useEffect(() => {
    if (isProcessing && jobProgress.completed > 0 && jobProgress.completed < jobProgress.total) {
      const elapsed = Date.now() - jobProgress.startTime;
      const timePerItem = elapsed / jobProgress.completed;
      const remaining = timePerItem * (jobProgress.total - jobProgress.completed);
      setEta(Math.round(remaining / 1000));
    } else if (!isProcessing) {
      setEta(null);
    }
  }, [jobProgress, isProcessing]);

  const handleClassify = async (email) => {
    try {
      // 1. Classify
      const classRes = await fetch(`${API_BASE}/emails/classify`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ subject: email.subject, body: email.body })
      })
      const classData = await classRes.json()

      // 2. Process/Archive
      await fetch(`${API_BASE}/emails/process`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: email.id, category: classData.category })
      })

      // Refresh stats perfectly from server
      await refreshStats()

    } catch (err) {
      console.error(err)
    } finally {
      setJobProgress(prev => ({ ...prev, completed: prev.completed + 1 }))
    }
  }

  const handlePullAndClassify = async () => {
    if (isProcessing) return
    setIsProcessing(true)
    setJobProgress({ total: 0, completed: 0, startTime: Date.now() })
    
    try {
      const res = await fetch(`${API_BASE}/emails/pull?count=${pullCount}`)
      const data = await res.json()
      const fetchedEmails = data.emails || []
      
      if (fetchedEmails.length === 0) {
        alert("No unprocessed emails found in inbox.")
        setIsProcessing(false)
        return
      }
      
      setJobProgress({ total: fetchedEmails.length, completed: 0, startTime: Date.now() })
      
      // Classify all fetched emails concurrently
      await Promise.all(fetchedEmails.map(email => handleClassify(email)))
    } catch (err) {
      console.error(err)
      alert("Process failed")
    }
    setIsProcessing(false)
  }

  const handleAddCategory = async (e) => {
    e.preventDefault()
    if (!newCat.name || !newCat.description) return
    try {
      await fetch(`${API_BASE}/categories`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newCat)
      })
      alert(`Category '${newCat.name}' added successfully!`)
      setNewCat({ name: '', description: '' })
    } catch (err) {
      console.error(err)
    }
  }

  return (
    <div className="app-container">
      <header>
        <h1>Gmail Classification Using Jev ⚡</h1>
        <p>Instant, AI-powered inbox zero with TypeSafe Codiv AI.</p>
      </header>

      <div className="dashboard-layout">
        
        {/* Left Column: Core Actions & Top Stats */}
        <div className="layout-column">
          <div className="hero-cta-section glass-panel" style={{ padding: '40px 20px', display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            
            {isProcessing && jobProgress.total > 0 ? (
              <div className="progress-container" style={{ marginBottom: '20px' }}>
                <div className="progress-stats">
                  <span>{jobProgress.completed} / {jobProgress.total} Classified</span>
                  <span>{eta !== null ? `ETA: ${eta}s` : 'Calculating...'}</span>
                </div>
                <div className="progress-bar-bg">
                  <div 
                    className="progress-bar-fill" 
                    style={{ width: `${(jobProgress.completed / jobProgress.total) * 100}%` }}
                  ></div>
                </div>
              </div>
            ) : (
              <div className="batch-size-selector" style={{ marginBottom: '20px' }}>
                <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '8px', display: 'block', textAlign: 'center' }}>SELECT BATCH SIZE</span>
                <div style={{ display: 'flex', gap: '10px' }}>
                  {[10, 25, 50, 100].map(val => (
                    <button 
                      key={val}
                      onClick={() => setPullCount(val)}
                      className={`batch-chip ${pullCount === val ? 'active' : ''}`}
                    >
                      {val}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <button className="mega-button" onClick={handlePullAndClassify} disabled={isProcessing} style={{ opacity: isProcessing ? 0.7 : 1, width: '100%' }}>
              {isProcessing ? '⚡ PROCESSING...' : '⚡ CLASSIFY EMAILS'}
            </button>
          </div>

          <div className="dashboard-stats glass-panel">
            <div className="stat-card">
              <h3>Emails Categorized</h3>
              <div className="value">{stats.categorized}</div>
            </div>
            <div className="stat-card">
              <h3>Tokens Consumed</h3>
              <div className="value" style={{color: '#2a8af6'}}>{stats.inputTokens.toLocaleString()}</div>
            </div>
            <div className="stat-card">
              <h3>Estimated Cost</h3>
              <div className="value" style={{color: '#e92a67'}}>
                ${(stats.inputTokens * 0.00000015).toFixed(5)}
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Categories */}
        <div className="layout-column">
          <div className="glass-panel" style={{padding: '20px', height: '100%', display: 'flex', flexDirection: 'column'}}>
            <h3 style={{marginTop: 0, marginBottom: '20px'}}>Classification Breakdown</h3>
            
            {Object.keys(stats.category_counts || {}).length === 0 ? (
              <p style={{color: 'var(--text-secondary)', textAlign: 'center', margin: 'auto'}}>No emails classified yet.</p>
            ) : (
              <div className="category-breakdown-grid">
                {Object.entries(stats.category_counts || {}).map(([cat, count]) => (
                  <div key={cat} className="category-rich-card">
                    <div className="cat-name">{cat}</div>
                    <div className="cat-count">{count}</div>
                  </div>
                ))}
              </div>
            )}
            
            <hr style={{ border: 'none', borderTop: '1px solid rgba(255,255,255,0.05)', margin: '30px 0' }} />
            
            <form className="add-category-form" onSubmit={handleAddCategory} style={{ marginTop: 'auto', padding: 0 }}>
              <h3 style={{ fontSize: '1.1rem' }}>✨ Train a New Category</h3>
              <div className="form-row" style={{ flexDirection: 'column' }}>
                <input 
                  placeholder="Category Name (e.g. 'newsletter')" 
                  value={newCat.name}
                  onChange={e => setNewCat({...newCat, name: e.target.value})}
                />
                <input 
                  placeholder="Description for the AI to understand..." 
                  value={newCat.description}
                  onChange={e => setNewCat({...newCat, description: e.target.value})}
                />
                <button type="submit" className="primary" style={{ marginTop: '10px' }}>Add Category</button>
              </div>
            </form>
          </div>
        </div>

      </div>

      <footer style={{ textAlign: 'center', marginTop: '60px', paddingBottom: '30px', color: 'var(--text-secondary)', fontSize: '0.9rem', borderTop: '1px solid rgba(255, 255, 255, 0.05)', paddingTop: '20px' }}>
        <p style={{ marginBottom: '8px' }}>
          Credits to <strong>OpenJev</strong> and <strong>Antigravity Google</strong> for supporting the development.
        </p>
        <p style={{ margin: 0, opacity: 0.7, fontSize: '0.8rem', lineHeight: '1.5' }}>
          &copy; {new Date().getFullYear()} Gmail Classification Using Jev. Open-source project released under the MIT License. <br/>
          View the source code and contribute on <a href="https://github.com/PrabaKDataScience/gmail_classifier" target="_blank" rel="noopener noreferrer" style={{ color: '#2a8af6', textDecoration: 'none', fontWeight: 'bold' }}>GitHub</a>.
        </p>
      </footer>
    </div>
  )
}

export default App
