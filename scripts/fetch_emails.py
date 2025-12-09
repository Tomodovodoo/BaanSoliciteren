"""Fetch emails from Gmail API and save to /Email/Processing."""
import os
import json
import base64
from pathlib import Path
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

SCRIPT_DIR = Path(__file__).parent
BASE_DIR = SCRIPT_DIR.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_DIR = BASE_DIR / "config"
EMAIL_DIR = BASE_DIR / "Email"
PROCESSING_DIR = EMAIL_DIR / "Processing"
LOG_FILE = DATA_DIR / "fetch_log.txt"
CONFIG_FILE = CONFIG_DIR / "fetch_emails_config.json"
CREDENTIALS_PATH = BASE_DIR / "credentials.json"
TOKEN_PATH = Path.home() / ".gmail-mcp" / "token.json"
UNRELATED_SENDERS_FILE = PROCESSING_DIR / "unrelated_email_senders.json"

# Job-related keywords for safety check
JOB_KEYWORDS = [
    'sollicitatie', 'vacature', 'application', 'vacancy',
    'interview', 'recruitment', 'career', 'job',
    'werving', 'selectie', 'hiring', 'baan',
]

def load_config():
    """Load configuration from config file."""
    if not CONFIG_FILE.exists():
        default_config = {
            "cutoff_date": "2025/11/19",
            "last_run": None
        }
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)
        return default_config
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    """Save configuration to config file."""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

def get_query():
    """Get query from command line or use date from config."""
    import sys
    if len(sys.argv) > 1:
        return sys.argv[1]
    
    config = load_config()
    cutoff_date = config.get('cutoff_date', '2025/11/19')
    return f"after:{cutoff_date}"

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError

# Scopes required for the script
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def load_credentials():
    """Load Gmail API credentials with auto-refresh and error handling."""
    creds = None
    
    if TOKEN_PATH.exists():
        try:
            with open(TOKEN_PATH, 'r') as f:
                token_data = json.load(f)
            creds = Credentials.from_authorized_user_info(token_data)
        except Exception:
            print("  Corrupt token file found. Deleting...")
            TOKEN_PATH.unlink()
            creds = None

    # If valid credentials (with refresh token) are present, verify validity
    if creds:
        if creds.expired and creds.refresh_token:
            try:
                print("  Refreshing expired access token...")
                creds.refresh(Request())
                # Save refreshed token
                with open(TOKEN_PATH, 'w') as f:
                    f.write(creds.to_json())
            except (RefreshError, Exception) as e:
                print(f"  Token refresh failed: {e}")
                print("  Deleting invalid token file to force re-authentication.")
                if TOKEN_PATH.exists():
                    TOKEN_PATH.unlink()
                creds = None
    
    # If no valid creds, trigger new auth flow
    if not creds:
        print("  Initiating new authentication flow...")
        if not CREDENTIALS_PATH.exists():
            raise FileNotFoundError(f"Credentials file not found at: {CREDENTIALS_PATH}")
            
        try:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(TOKEN_PATH, 'w') as f:
                f.write(creds.to_json())
                
        except Exception as e:
            print(f"  Authentication failed: {e}")
            raise
        
    return creds

def decode_body(payload):
    """Extract and decode email body from payload."""
    body = ""
    
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                if 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                    break
            elif part['mimeType'] == 'multipart/alternative' and 'parts' in part:
                for subpart in part['parts']:
                    if subpart['mimeType'] == 'text/plain' and 'data' in subpart['body']:
                        body = base64.urlsafe_b64decode(subpart['body']['data']).decode('utf-8', errors='ignore')
                        break
    elif 'body' in payload and 'data' in payload['body']:
        body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8', errors='ignore')
    
    return body

def get_header(headers, name):
    """Extract header value by name."""
    for header in headers:
        if header['name'].lower() == name.lower():
            return header['value']
    return None

def load_spam_list():
    """Load list of unrelated email senders."""
    if not UNRELATED_SENDERS_FILE.exists():
        return []
    with open(UNRELATED_SENDERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_email(from_field):
    """Extract email address from 'From' field."""
    if not from_field:
        return None
    
    import re
    # Look for email in angle brackets
    match = re.search(r'<([^>]+)>', from_field)
    if match:
        return match.group(1).strip().lower()
    
    # Otherwise assume entire field is email
    return from_field.strip().lower()

def is_spam_sender(email_from, subject, spam_list):
    """Check if email is from known spam sender."""
    sender_email = extract_email(email_from)
    if not sender_email:
        return False
    
    # Check against spam list
    if sender_email in spam_list:
        # Safety check: never filter job-related emails
        subject_lower = (subject or '').lower()
        for keyword in JOB_KEYWORDS:
            if keyword in subject_lower:
                return False  # Don't filter job-related keywords
        return True
    
    return False

def fetch_emails():
    """Fetch emails from Gmail and save to Processing folder."""
    runtime_date = datetime.now()
    runtime_date_str = runtime_date.strftime("%Y/%m/%d")
    
    print("Loading credentials...")
    creds_or_service = load_credentials()
    
    print("Connecting to Gmail API...")
    if hasattr(creds_or_service, 'users'):
        service = creds_or_service
    else:
        service = build('gmail', 'v1', credentials=creds_or_service)
    
    query = get_query()
    print(f"Fetching emails (query: '{query}')...")
    
    all_messages = []
    page_token = None
    page_count = 0
    
    while True:
        page_count += 1
        print(f"  Fetching page {page_count}...")
        
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=100,
            pageToken=page_token
        ).execute()
        
        messages = results.get('messages', [])
        all_messages.extend(messages)
        
        page_token = results.get('nextPageToken')
        if not page_token:
            break
    
    print(f"Found {len(all_messages)} total emails across {page_count} page(s).")
    
    if not all_messages:
        print("No emails to process.")
        config = load_config()
        config['cutoff_date'] = runtime_date_str
        config['last_run'] = runtime_date.isoformat()
        save_config(config)
        print(f"\n✓ Updated cutoff date to: {runtime_date_str}")
        return
    
    # Load spam filter
    spam_list = load_spam_list()
    if spam_list:
        print(f"  Loaded spam filter with {len(spam_list)} blocked senders\n")
    
    PROCESSING_DIR.mkdir(parents=True, exist_ok=True)
    
    processed, skipped, filtered_spam = 0, 0, 0
    
    for msg in all_messages:
        email_id = msg['id']
        output_file = PROCESSING_DIR / f"{email_id}.json"
        
        if output_file.exists():
            skipped += 1
            continue
        
        email = service.users().messages().get(
            userId='me',
            id=email_id,
            format='full'
        ).execute()
        
        headers = email['payload']['headers']
        
        # Check spam filter
        email_from = get_header(headers, 'From')
        email_subject = get_header(headers, 'Subject')
        
        if spam_list and is_spam_sender(email_from, email_subject, spam_list):
            filtered_spam += 1
            if filtered_spam <= 3:  # Show first 3 filtered emails
                print(f"  ✓ Filtered spam: {email_subject[:50]}")
            continue
        
        email_data = {
            "email_id": email_id,
            "thread_id": email.get('threadId', ''),
            "date": get_header(headers, 'Date'),
            "from": get_header(headers, 'From'),
            "to": get_header(headers, 'To'),
            "subject": get_header(headers, 'Subject'),
            "snippet": email.get('snippet', ''),
            "body": decode_body(email['payload']),
            "response": None,
            "company": None,
            "assigned": False
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(email_data, f, indent=2, ensure_ascii=False)
        
        processed += 1
        if processed % 10 == 0:
            print(f"  [{processed}/{len(all_messages)}] Processing...")
    
    print(f"\n✓ Complete! Processed: {processed}, Skipped: {skipped}")
    if filtered_spam > 0:
        print(f"✓ Filtered spam: {filtered_spam} emails")
    print(f"  Output: {PROCESSING_DIR.absolute()}")
    
    config = load_config()
    config['cutoff_date'] = runtime_date_str
    config['last_run'] = runtime_date.isoformat()
    save_config(config)
    print(f"\n✓ Updated cutoff date to: {runtime_date_str}")

if __name__ == "__main__":
    try:
        fetch_emails()
    except Exception as e:
        print(f"ERROR: {e}")
        exit(1)
