from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# Import our existing scripts
from pull_emails import pull_mails, get_gmail_service
from label_emails import apply_labels_to_email
from typesafe_sdk import Choice, TypeSafeClient
from logger import get_logger

load_dotenv()

logger = get_logger()
app = FastAPI(title="Gmail AI Classifier API")

# Configure CORS for our frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Codiv AI Client
try:
    client = TypeSafeClient()
    logger.info("Successfully initialized TypeSafeClient.")
except Exception as e:
    logger.error(f"Error initializing TypeSafeClient: {e}")
    client = None

# Pydantic models for request validation
class EmailToClassify(BaseModel):
    subject: str
    body: str

class EmailToProcess(BaseModel):
    id: str
    category: str

@app.get("/api/status")
async def get_status():
    """Check if Gmail OAuth and Codiv API are configured."""
    has_gmail_token = os.path.exists("token.json")
    has_codiv_key = bool(os.getenv("TYPESAFE_API_KEY"))
    
    return {
        "gmail_connected": has_gmail_token,
        "codiv_api_ready": has_codiv_key,
        "status": "ready" if has_gmail_token and has_codiv_key else "setup_required"
    }

@app.get("/api/emails/pull")
async def pull_emails_endpoint(count: int = 5):
    """Pull recent unprocessed emails from Gmail."""
    try:
        logger.info(f"Pulling up to {count} emails from Gmail...")
        emails = pull_mails(no_of_mails=count)
        logger.info(f"Successfully pulled {len(emails) if emails else 0} emails.")
        return {"emails": emails or []}
    except Exception as e:
        logger.error(f"Failed to pull emails: {e}")
        raise HTTPException(status_code=500, detail=str(e))

import json
import os

STATE_FILE = "state.json"

# Default state
app_state = {
    "categories": {
        "banking": "Banking alerts, account statements, financial transactions, OTPs",
        "ecommerce": "Order confirmations, shipping updates, product promotions, online shopping",
        "recruitment": "Job opportunities, interview scheduling, recruiter messages",
        "tech community": "Tech newsletters, developer forum updates, programming community discussions",
        "travel": "Flight tickets, hotel bookings, travel itineraries, vacation planning",
        "other": "Emails that do not fit into any of the specific categories above"
    },
    "stats": {
        "categorized": 0,
        "inputTokens": 0,
        "outputTokens": 0,
        "category_counts": {}
    }
}

# Load state from disk
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        try:
            loaded_state = json.load(f)
            app_state.update(loaded_state)
        except Exception:
            pass

def save_state():
    with open(STATE_FILE, "w") as f:
        json.dump(app_state, f)

class NewCategory(BaseModel):
    name: str
    description: str

@app.get("/api/categories")
async def get_categories():
    """Returns the current list of categories."""
    return {"categories": app_state["categories"]}

@app.get("/api/stats")
async def get_stats():
    """Returns the current persistent stats."""
    return {"stats": app_state["stats"]}

@app.post("/api/categories")
async def add_category(category: NewCategory):
    """Add a new category to the classification criteria."""
    cat_name = category.name.lower()
    app_state["categories"][cat_name] = category.description
    if cat_name not in app_state["stats"]["category_counts"]:
        app_state["stats"]["category_counts"][cat_name] = 0
    save_state()
    return {"success": True, "categories": app_state["categories"]}

@app.post("/api/emails/classify")
async def classify_email(email: EmailToClassify):
    """Classify a single email using Codiv AI System One."""
    if not client:
        logger.error("TypeSafeClient is not initialized, cannot classify.")
        raise HTTPException(status_code=500, detail="TypeSafeClient not initialized. Check API keys.")
        
    content_to_classify = f"Subject: {email.subject}\nBody: {email.body}"
    logger.info(f"Classifying email: '{email.subject}'...")
    
    try:
        response = client.system_one(
            content_to_classify,
            {
                "category": Choice(
                    instructions="Classify this email into the correct category based on its content.",
                    criteria=app_state["categories"],
                )
            },
            model="openjev-latest",
        )
        
        predicted_category = response.choices["category"].choice
        usage = response.usage
        in_tokens = usage.input_tokens if hasattr(usage, "input_tokens") else 0
        out_tokens = usage.output_tokens if hasattr(usage, "output_tokens") else 0
        
        app_state["stats"]["inputTokens"] += in_tokens
        app_state["stats"]["outputTokens"] += out_tokens
        save_state()
        
        logger.info(f"Email classified as '{predicted_category}' (Tokens: In={in_tokens}, Out={out_tokens})")
        
        return {
            "category": predicted_category,
            "usage": {
                "input_tokens": in_tokens,
                "output_tokens": out_tokens
            }
        }
        
    except Exception as e:
        logger.error(f"Classification failed for email '{email.subject}': {e}")
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@app.post("/api/emails/process")
async def process_email(email: EmailToProcess):
    """Apply labels and archive the email based on its category."""
    logger.info(f"Processing and labeling email {email.id} as '{email.category}'...")
    try:
        service = get_gmail_service()
        if not service:
            logger.error("Gmail authentication failed during processing.")
            raise HTTPException(status_code=401, detail="Gmail authentication failed")
            
        apply_labels_to_email(service, email.id, email.category)
        
        # Update stats
        cat_key = email.category.lower()
        if cat_key not in app_state["stats"]["category_counts"]:
            app_state["stats"]["category_counts"][cat_key] = 0
            
        app_state["stats"]["categorized"] += 1
        app_state["stats"]["category_counts"][cat_key] += 1
        save_state()
        
        logger.info(f"Successfully processed email {email.id}.")
        return {"success": True, "message": f"Applied '{email.category}' label and archived message {email.id}"}
    except Exception as e:
        logger.error(f"Error processing email {email.id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
