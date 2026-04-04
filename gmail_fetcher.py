import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_gmail_service():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def get_body(payload):
    body = ""
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                    break
    else:
        data = payload['body'].get('data', '')
        if data:
            body = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
    return body.strip()

def fetch_emails(max_emails=10):
    service = get_gmail_service()
    results = service.users().messages().list(
        userId='me',
        maxResults=max_emails,
        labelIds=['INBOX']
    ).execute()

    messages = results.get('messages', [])
    emails = []

    for i, msg in enumerate(messages):
        data = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()

        headers = data['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        body = get_body(data['payload'])

        emails.append({
            "email_id": i + 1,
            "subject": subject,
            "sender": sender,
            "body": body[:500],
            "gmail_id": msg['id']
        })
        print(f"✅ Fetched: {subject[:50]}")

    return emails

if __name__ == "__main__":
    emails = fetch_emails(5)
    print(f"\nTotal fetched: {len(emails)}")
    for e in emails:
        print(f"- {e['subject'][:50]}")