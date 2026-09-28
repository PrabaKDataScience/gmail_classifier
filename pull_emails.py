import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json

# If modifying these scopes, delete the file token.json.
# We need modify access to messages to apply labels after classification
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_gmail_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists('credentials.json'):
                print("ERROR: 'credentials.json' not found!")
                print("Please download it from Google Cloud Console and place it in this directory.")
                return None
                
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        return service
    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def extract_message_body(payload):
    """
    Recursively parse the email payload to find the plain text body.
    Falls back to HTML (with tags stripped using BeautifulSoup) if plain text is not available.
    """
    import base64

    body_text = ""
    body_html = ""

    def traverse(parts):
        nonlocal body_text, body_html
        for part in parts:
            mimeType = part.get('mimeType')
            data = part.get('body', {}).get('data')
            
            if mimeType == 'text/plain' and data:
                body_text = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            elif mimeType == 'text/html' and data:
                # Keep the first html part we find if we haven't found one yet
                if not body_html:
                    body_html = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            elif 'parts' in part:
                traverse(part['parts'])

    if 'parts' in payload:
        traverse(payload['parts'])
    else:
        mimeType = payload.get('mimeType')
        data = payload.get('body', {}).get('data')
        if data:
            decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            if mimeType == 'text/plain':
                body_text = decoded
            elif mimeType == 'text/html':
                body_html = decoded

    final_text = body_text if body_text else body_html

    if final_text:
        try:
            from bs4 import BeautifulSoup
            # Parse even plain text as HTML to unescape entities like &nbsp; and remove errant tags
            soup = BeautifulSoup(final_text, "html.parser")
            # Remove script and style elements so CSS/JS doesn't leak into the text
            for script_or_style in soup(['script', 'style']):
                script_or_style.decompose()
            text = soup.get_text(separator=' ', strip=True)
            import re
            text = re.sub(r'\s+', ' ', text)
            text = text.encode('ascii', 'ignore').decode('ascii')
            return text.strip()
        except ImportError:
            return final_text
        
    return ""

def pull_recent_emails(service, max_results=5):
    """
    Pulls the most recent emails from INBOX and formats them.
    """
    try:
        # Fetch the list of messages in INBOX that don't have the 'processed' label
        results = service.users().messages().list(
            userId='me', 
            labelIds=['INBOX'], 
            q='-label:processed',
            maxResults=max_results
        ).execute()
        messages = results.get('messages', [])

        if not messages:
            print('No messages found.')
            return []

        formatted_emails = []

        print(f"Pulling {len(messages)} recent emails...")
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
            payload = msg.get('payload', {})
            headers = payload.get('headers', [])
            
            # Find the Subject
            subject = "No Subject"
            for header in headers:
                if header['name'].lower() == 'subject':
                    subject = header['value']
                    break
                    
            # Extract Body
            body = extract_message_body(payload)
            
            formatted_emails.append({
                "id": message['id'],
                "subject": subject,
                "body": body.strip()
            })
            
        return formatted_emails

    except HttpError as error:
        print(f'An error occurred while fetching emails: {error}')
        return []

import re

def truncate_body_for_classification(mail_data, max_length=200):
    """
    Truncates the 'body' field of each email dictionary in the list to a specified maximum length.
    Removes URLs, bracketed text, repetitive punctuation, and normalizes excessive whitespace 
    to ensure the 200 character limit captures actual useful text.
    Useful for limiting the amount of text sent to a classification model.
    """
    for email in mail_data:
        body = email.get('body', '')
        if body:
            # Remove URLs
            body = re.sub(r'http[s]?://\S+|www\.\S+', '', body)
            # Remove markdown links or bracketed navigational text (e.g., [Sign in])
            body = re.sub(r'\[.*?\]', '', body)
            # Remove repetitive punctuation like --- or ***
            body = re.sub(r'[-=*_]{2,}', '', body)
            # Replace all consecutive whitespace (including newlines) with a single space and strip edges
            cleaned_body = re.sub(r'\s+', ' ', body).strip()
            email['body'] = cleaned_body[:max_length]
    return mail_data

def pull_mails(no_of_mails = 3):
    service = get_gmail_service()
    if service:
        emails = pull_recent_emails(service, max_results=no_of_mails)
        
        # Print out the formatted list to match our mock data structure
        print("\n=== Pulled Emails Data Structure ===\n")
        sliced_mail_data = truncate_body_for_classification(emails, max_length=200)
        # Print it out as JSON so we can see it, but return the actual Python list of dictionaries
        print(json.dumps(sliced_mail_data, indent=4))
        return sliced_mail_data

