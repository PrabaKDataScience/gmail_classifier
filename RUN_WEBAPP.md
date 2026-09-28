# Running the Gmail AI Classifier Web App 🚀

This project features a decoupled architecture with a Python **FastAPI** backend and a **Vite (React)** frontend. You will need to start both services to use the dashboard.

## 1. Start the Backend (FastAPI)

The backend exposes the Gmail integration and TypeSafe AI logic via REST API on `localhost:8000`.

1. Open your terminal.
2. Ensure you are in the root directory (`d:\gmail_classifier`).
3. Run the following command using `uv` to start the server:

```bash
uv run uvicorn main:app --reload
```

*The `--reload` flag means the server will automatically restart if you make any changes to `main.py`.*

## 2. Start the Frontend (React + Vite)

The frontend is a modern, glassmorphism dashboard that runs on `localhost:5173`.

1. Open a **new** terminal window.
2. Navigate into the frontend folder:
   ```bash
   cd d:\gmail_classifier\frontend
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```

## 3. Access the Dashboard

Once both servers are running, open your web browser and navigate to:

👉 **[http://localhost:5173](http://localhost:5173)**

### Troubleshooting
- **No Emails Showing?** Check the backend terminal for logs to ensure your `token.json` is valid.
- **Classification Failing?** Ensure your Codiv AI token is present in the `.env` file and that you have remaining quota.
- **API Errors?** Make sure the backend is still running in the first terminal.
