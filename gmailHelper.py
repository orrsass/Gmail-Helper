import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle
from gpt4all import GPT4All


class Email:
    def __init__(self, subject, sender, category=None, priority=None, action_required=False):
        """
        Initialize an Email object with its properties.
        """
        self.subject = subject
        self.sender = sender
        self.category = category  # e.g., "Work", "Personal", etc.
        self.priority = priority  # e.g., "Urgent", "Important", "Normal"
        self.action_required = action_required  # Boolean

    def __repr__(self):
        """
        String representation for debugging and printing.
        """
        return (f"Email (subject:'{self.subject}', sender:'{self.sender}', "
                f"category:'{self.category}', priority:'{self.priority}', "
                f"action_required:{self.action_required})")


# Define the Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def authenticate_gmail():
    """
    Authenticate with Gmail API using credentials.json.
    Returns the Gmail API service object.
    """
    creds = None

    # Check if token.pickle exists, and if so, use it to authorize
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If no valid credentials available, prompt the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Load credentials from the credentials.json file
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Build and return the Gmail API service
    return build('gmail', 'v1', credentials=creds)


def get_emails(service, max_results=10):
    """
    Fetches the latest 'max_results' emails from the user's Gmail inbox.
    """
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


def interact_with_llm(subject, sender, predefined_categories):
    """Send the email subject and sender to the LLM and return its response."""
    model = GPT4All("Phi-3-mini-4k-instruct.Q4_0.gguf")
    with model.chat_session():
        prompt = (f"i got this Email from '{sender}' with subject: '{subject}' .\n"
                  f"Predefined Categories: {predefined_categories}\n"
                  f"Please categorize this email into one of the predefined categories if you find relevant one.\n"
                  f"If none relevant, suggest a new category.\n"
                  f"in addition to that rank its priority (Urgent, Normal, Spam)."
                  f" State if a follow-up action is required only if: \n"
                  f"-The email requests an explicit response or task from you.\n"
                  f"- The email contains time-sensitive information that demands your attention.\n"
                  f" fill that format:'Category: [Category]\n Priority: [Priority]\n Action Required? : [Yes/No].\n"
                  f" do not add any explanation or extra words. only the format above.")

        output = (model.generate(prompt=prompt, max_tokens=50))

        return output


def main():
    """
    Main function to authenticate Gmail and fetch emails.
    """
    try:
        # Authenticate with Gmail and get the service object
        service = authenticate_gmail()

        # Fetch the latest emails
        emails = get_emails(service, max_results=5)
        mails = []
        categories = {"Work": [],
                      "Personal": [],
                      "Shopping": [],
                      "Travel": [],
                      "Finance": [],
                      "Health": []}
        predefined_categories = list(categories.keys())

        print(f"Fetched {len(emails)} emails.")

        # Print out subject and sender of each email
        for email in emails:
            mail = Email(email['subject'], email['sender'])
            print(f"mail = {email['subject'], email['sender']}")
            output = interact_with_llm(email['subject'], email['sender'], predefined_categories)
            print(f"output = {output}")

            lines = output.strip().split('\n')
            for line in lines:
                if line.startswith("Category:"):
                    mail.category = line.split(":")[1].strip()
                    if mail.category in predefined_categories:
                        categories[mail.category].append(mail)
                    else:
                        categories[mail.category] = [mail]
                elif line.startswith("Priority:"):
                    mail.priority = line.split(":")[1].strip()
                elif line.startswith("Action Required?"):
                    mail.action_required = line.split(":")[1].strip() == "Yes"
            mails.append(mail)
        print(mails)

        print(categories["Finance"])

        action_required_emails = [mail for mail in mails if mail.action_required is True]

        # Display the emails requiring action
        print("\nEmails Requiring Action:")
        for mail in action_required_emails:
            print(f"{mail}\n")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    main()
