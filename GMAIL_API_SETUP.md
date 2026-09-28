# Gmail API Setup Guide

This guide explains how to set up your Google Cloud project, obtain the necessary `credentials.json` file, and generate the `token.json` file required to give your script permission to read and modify your emails.

### Step 1: Create a Google Cloud Project
1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Log in with your Google account.
3. In the top-left corner, click the **Project drop-down** and select **New Project**.
4. Name your project (e.g., `Email Classifier`) and click **Create**.

### Step 2: Enable the Gmail API
1. In the Google Cloud Console, make sure your new project is selected at the top.
2. Open the navigation menu (the hamburger icon on the top left) and go to **APIs & Services > Library**.
3. Search for **"Gmail API"**.
4. Click on **Gmail API** and then click the blue **Enable** button.

### Step 3: Configure the OAuth Consent Screen
1. Go to **APIs & Services > OAuth consent screen**.
2. Select **External** (or Internal if you are using a Google Workspace company account) and click **Create**.
3. Fill out the required fields:
   - **App name:** `Email Classifier`
   - **User support email:** Select your email address
   - **Developer contact information:** Type your email address
4. Click **Save and Continue**.
5. On the **Scopes** screen, just click **Save and Continue** (we define the scopes directly in our Python script).
6. On the **Test users** screen, click **Add Users** and type in your own Gmail address. *(This is crucial! Because your app isn't publicly published, only the test users you list here will be allowed to log in).*
7. Click **Save and Continue**, then review and return to the dashboard.

### Step 4: Create OAuth Credentials (`credentials.json`)
1. Go to **APIs & Services > Credentials**.
2. Click the **+ CREATE CREDENTIALS** button at the top and select **OAuth client ID**.
3. For **Application type**, select **Desktop app**.
4. Give it a name (e.g., `Desktop Classifier`) and click **Create**.
5. A modal will pop up with your Client ID and Client Secret. Click the **Download JSON** button to download your credentials.
6. **Rename** the downloaded file to exactly `credentials.json`.
7. **Move** `credentials.json` into your working folder (`d:\for_tamil_ai\openjev-exploration\`).

### Step 5: Generate `token.json`
1. Make sure you delete any old `token.json` file in your folder if you already had one.
2. Open your terminal in the `openjev-exploration` folder and run your script:
   ```bash
   uv run mock_classification.py
   ```
3. Because `token.json` is missing, the script will automatically open a new tab in your web browser.
4. You will be prompted to log in to your Google account.
5. Because this is your own private app, Google will show a warning saying **"Google hasn't verified this app."** 
   - Click **Advanced** at the bottom.
   - Click **Go to Email Classifier (unsafe)**.
6. Check the boxes to grant the application permission to read and modify your emails.
7. Click **Continue**.
8. The browser will say "The authentication flow has completed. Please close this window."
9. If you look in your `openjev-exploration` folder, a brand new **`token.json`** file has been automatically created!

