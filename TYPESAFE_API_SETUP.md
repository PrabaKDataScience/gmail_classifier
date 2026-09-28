# TypeSafe API Setup Guide

This guide explains how to generate the necessary `TYPESAFE_API_KEY` for the Codiv API and configure it in your project.

### Step 1: Log in to Codiv AI Dashboard
Navigate to the Codiv AI platform (usually located at [codiv.ai](https://codiv.ai) or the developer portal matching the base URL `https://api.codiv.ai`) and log in to your account.

### Step 2: Navigate to API Settings
Look for a section titled **API Keys**, **Developer Settings**, or **Tokens** in your account dashboard or profile menu.

### Step 3: Generate a New Key
1. Click the button to **Create New Secret Key** or **Generate API Key**.
2. You may be prompted to give the key a name (e.g., `Gmail Classifier Project`).
3. Confirm the creation.

### Step 4: Copy the Key
Once the key is generated, copy it immediately. It will typically start with `sk-codiv-`. 
*Note: For security reasons, most platforms will only show this key to you once. If you lose it, you will need to generate a new one.*

### Step 5: Update Your `.env` File
Create or open the `.env` file in the root directory of your project, and paste the copied key along with the base URL:

```env
TYPESAFE_API_KEY="sk-codiv-YOUR_NEW_KEY_HERE"
TYPESAFE_BASE_URL="https://api.codiv.ai"
```

Once saved, your scripts using `typesafe_sdk` will automatically authenticate with the Codiv API.
