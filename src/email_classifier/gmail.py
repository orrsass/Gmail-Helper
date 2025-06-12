import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from .config import GOOGLE_CREDENTIALS_PATH

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                GOOGLE_CREDENTIALS_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)

def get_emails(service, max_results=100):
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])
    email_data = []
    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_detail.get('payload', {}).get('headers', [])
        subject = sender = None
        for header in headers:
            if header['name'] == 'Subject':
                subject = header['value']
            if header['name'] == 'From':
                sender = header['value']
        email_data.append({'subject': subject, 'sender': sender})
    return email_data 