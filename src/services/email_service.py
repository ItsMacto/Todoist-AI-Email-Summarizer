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
                    # Request offline access so that we get a refresh token.
                    self.creds = flow.run_local_server(port=0, access_type='offline', prompt='consent')
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
        Uses Gmail's query syntax for filtering based on configuration.
        """
        if not self.service:
            logger.error("Gmail service not connected.")
            return []

        try:
            # Load configuration to get filtering options
            from src.config.manager import ConfigManager
            config = ConfigManager().load_config()

            filters = [f"newer_than:{days}d"]

            # If EXCLUDE_READ is true, only fetch unread OR important emails.
            if config.get('EXCLUDE_READ', 'yes').lower() == 'yes':
                filters.append("((is:unread) OR (is:important))")

            # If EXCLUDE_SPAM is true, exclude spam.
            if config.get('EXCLUDE_SPAM', 'yes').lower() == 'yes':
                filters.append("-in:spam")

            # If EXCLUDE_PROMOTIONAL is true, exclude promotional emails.
            if config.get('EXCLUDE_PROMOTIONAL', 'yes').lower() == 'yes':
                filters.append("-category:promotions")

            # Combine filters into a query string
            query = " ".join(filters)
            logger.info(f"Gmail query: {query}")

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
                # Determine if the email is marked as important
                important = any(h.get('name', '').lower() == 'importance' and 'important' in h.get('value', '').lower() for h in headers)
                body = msg.get('snippet', '')

                emails.append({
                    'subject': subject,
                    'from': sender,
                    'date': date,
                    'body': body,
                    'important': important
                })
            return emails

        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return []