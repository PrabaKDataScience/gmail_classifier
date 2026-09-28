# Gmail AI Classifier 🤖📧

An intelligent email automation tool that leverages the Gmail API and the **TypeSafe SDK** (Codiv AI) to automatically categorize, label, and archive incoming emails. Keep your inbox zeroed out by routing emails into smart categories like Banking, E-commerce, Recruitment, and Tech Community without manual intervention.

---

## 🌟 Features

- **Automated Pulling**: Securely connects to your Gmail INBOX and fetches unread/unprocessed messages.
- **Cognitive Architecture (System One)**: Utilizes the `client.system_one()` method to perform rapid, intuitive classification, simulating human fast-thinking.
- **OpenJev Model**: Powered by `openjev-latest`, an advanced model optimized for high-speed, accurate semantic routing and decision making.
- **Auto-Labeling & Archiving**: Dynamically creates required Gmail labels (if they don't exist), applies them to the email thread, and archives the message out of your INBOX.
- **Type-Safe Parsing**: Enforces strict category structures using the TypeSafe framework to prevent hallucinated labels and ensure output predictability.

## 🛠 Project Structure

```text
├── classify_mails.py       # Main entry point for pulling, classifying, and labeling emails
├── pull_emails.py          # Gmail API integration for fetching and parsing email bodies
├── label_emails.py         # Gmail API integration for applying labels and modifying threads
├── first_try.py            # Sandbox script demonstrating TypeSafe SDK capabilities
├── GMAIL_API_SETUP.md      # Documentation for Google Cloud / OAuth setup
├── TYPESAFE_API_SETUP.md   # Documentation for Codiv API key generation
├── pyproject.toml          # uv project configuration and dependencies
└── uv.lock                 # Strict dependency lockfile
```

## 📋 Prerequisites

- **Python 3.12+**
- **uv**: Lightning-fast Python package installer and resolver.
- **Google Cloud Console Account**: For generating Gmail API OAuth credentials.
- **Codiv AI Account**: For generating the `TYPESAFE_API_KEY`.

## 🚀 Installation & Setup

1. **Clone the repository** (if applicable) and navigate to the project directory:
   ```bash
   cd gmail_classifier
   ```

2. **Install dependencies** using `uv`:
   ```bash
   uv sync
   ```
   *(This will automatically create a `.venv` and install all required packages).*

## ⚙️ Configuration

### 1. Gmail API Credentials
You need a `credentials.json` file to authenticate with Google. 
- Please refer to [GMAIL_API_SETUP.md](./GMAIL_API_SETUP.md) for detailed step-by-step instructions.
- Upon first execution, a browser window will prompt you to authorize the app. A `token.json` file will then be generated to maintain your session.

### 2. TypeSafe API Settings
Create a `.env` file in the root of the project with your Codiv AI credentials:
- Please refer to [TYPESAFE_API_SETUP.md](./TYPESAFE_API_SETUP.md) for instructions on generating your key.
```env
TYPESAFE_API_KEY="sk-codiv-YOUR_API_KEY"
TYPESAFE_BASE_URL="https://api.codiv.ai"
```

## 💻 Usage

To run the classifier pipeline and process your recent emails:

```bash
uv run classify_mails.py
```

**Workflow:**
1. Connects to your Gmail inbox and pulls the latest emails lacking the `processed` label.
2. Truncates and cleans the email body for efficient AI processing.
3. Sends the email text to the Codiv AI model for classification.
4. Identifies the predicted category (e.g., *Banking*, *E-commerce*).
5. Applies the respective category label and a `processed` label to the entire email thread.
6. Removes the thread from your `INBOX`.

## 🛡️ Security Note

This repository contains `.gitignore` rules to prevent the accidental upload of `.env`, `credentials.json`, `token.json`, and `.venv`. Never commit your private API keys or OAuth tokens to version control.
