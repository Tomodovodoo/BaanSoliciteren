"""Fetch emails from Gmail API and save to /Email/Processing."""
import os
import json
import base64
from pathlib import Path
from datetime import datetime
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials

CREDENTIALS_PATH = Path("credentials.json")
TOKEN_PATH = Path.home() / ".gmail-mcp" / "token.json"
OUTPUT_DIR = Path("Email/Processing")
CONFIG_PATH = Path("config/fetch_emails_config.json")

def load_config():
    """Load configuration from config file."""
    if not CONFIG_PATH.exists():
        default_config = {
            "cutoff_date": "2025/11/19",
            "last_run": None
        }
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)
        return default_config
    
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    """Save configuration to config file."""
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

def get_query():
    """Get query from command line or use date from config."""
    import sys
    if len(sys.argv) > 1:
        return sys.argv[1]
    
    config = load_config()
    cutoff_date = config.get('cutoff_date', '2025/11/19')
    return f"after:{cutoff_date}"

def load_credentials():
    """Load Gmail API credentials."""
    if TOKEN_PATH.exists():
        with open(TOKEN_PATH, 'r') as f:
            token_data = json.load(f)
        creds = Credentials.from_authorized_user_info(token_data)
        return creds
    
    from gmail_mcp.utils.GCP.gmail_auth import get_gmail_service
    os.environ['GMAIL_CREDENTIALS_PATH'] = str(CREDENTIALS_PATH)
    return get_gmail_service()

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
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    processed, skipped = 0, 0
    
    for msg in all_messages:
        email_id = msg['id']
        output_file = OUTPUT_DIR / f"{email_id}.json"
        
        if output_file.exists():
            skipped += 1
            continue
        
        email = service.users().messages().get(
            userId='me',
            id=email_id,
            format='full'
        ).execute()
        
        headers = email['payload']['headers']
        
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
    print(f"  Output: {OUTPUT_DIR.absolute()}")
    
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
