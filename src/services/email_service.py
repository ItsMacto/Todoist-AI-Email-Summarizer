import os
import pickle
from datetime import datetime, timedelta
from src.utils.logger import logger

# Import Google API client libraries
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build


class EmailService:
    """
    Handles email operations using the Gmail API with OAuth2.
    This service loads OAuth credentials (or initiates the OAuth flow if needed),
    builds a Gmail API service, and then queries emails received in the last `days` days.
    """

    # If you only need read access, this scope is sufficient.
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    def __init__(self):
        # Token file stores the user's access and refresh tokens.
        self.token_file = 'token.json'
        # This file should be downloaded from Google Cloud Console
        self.credentials_file = 'credentials.json'
        self.creds = None
        self.service = None

    def connect(self):
        """Establish a connection to Gmail via the API using OAuth2."""
        try:
            # Check if token file exists.
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    self.creds = pickle.load(token)
            # If there are no (valid) credentials, let the user log in.
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, self.SCOPES)
                    self.creds = flow.run_local_server(port=0)
                # Save the credentials for the next run.
                with open(self.token_file, 'wb') as token:
                    pickle.dump(self.creds, token)
            self.service = build('gmail', 'v1', credentials=self.creds)
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Gmail API: {e}")
            return False

    def disconnect(self):
        """
        For the Gmail API, there's no persistent connection to close.
        We'll simply delete the service instance.
        """
        self.service = None

    def fetch_recent_emails(self, days=1):
        """
        Fetch emails received in the last `days` days.
        Uses Gmail's query syntax ("newer_than:Nd") for filtering.
        """
        if not self.service:
            logger.error("Gmail service not connected.")
            return []

        try:
            # Use Gmail search query to get messages newer than the specified days.
            query = f"newer_than:{days}d"
            results = self.service.users().messages().list(userId='me', q=query).execute()
            messages = results.get('messages', [])
            emails = []

            for message in messages:
                msg = self.service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                payload = msg.get('payload', {})
                headers = payload.get('headers', [])
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No subject')
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown sender')
                date = next((h['value'] for h in headers if h['name'].lower() == 'date'), '')
                # For simplicity, we use the Gmail snippet as the email body.
                body = msg.get('snippet', '')
                emails.append({
                    'subject': subject,
                    'from': sender,
                    'date': date,
                    'body': body
                })
            return emails

        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []