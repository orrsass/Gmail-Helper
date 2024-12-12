import base64
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle
from gpt4all import GPT4All
import redis
import json
import hashlib
from datetime import timedelta
import matplotlib.pyplot as plt
from tqdm import tqdm

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)


def hash_request(subject, sender, predefined_categories, task):
    """
    Create a unique hash for the LLM request to use as a Redis key.
    """
    request_string = f"{subject}|{sender}|{'|'.join(predefined_categories)}|{task}"
    return hashlib.sha256(request_string.encode()).hexdigest()


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
        return (f"\nsubject:'{self.subject}'\nsender:'{self.sender}'\n"
                f"category:'{self.category}'\npriority:'{self.priority}'\n"
                f"action_required:{self.action_required}")


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


def interact_with_llm(subject, sender, predefined_categories, task):
    """Send the email subject and sender to the LLM and return its response."""
    # Create a unique key for this request
    request_key = hash_request(subject, sender, predefined_categories, task)
    # Check if the response is in Redis
    cached_response = redis_client.get(request_key)
    if cached_response:
        print("Using cached response.")
        return cached_response.decode()  # Return the cached response as a string

    if task == "category":
        prompt = ("Categorize the following email concisely.\n\n"
                  f"Sender: '{sender}'\n"
                  f"Subject: '{subject}'\n"
                  f"Predefined Categories: {predefined_categories}\n\n"
                  "Task: Select the most relevant category from the predefined list, "
                  "or suggest a new category if none apply.\n"
                  "Output Format: 'Category: [Category]'.\n"
                  "Do not include any explanations or additional text.")
    elif task == "priority":
        prompt = ("Determine the priority of the following email on a scale of 1-10 (10 is urgent, 1 can wait):\n\n"
                  f"Sender: '{sender}'\n"
                  f"Subject: '{subject}'\n\n"
                  "Criteria:\n"
                  "- Emails from individuals have a higher priority than those from newsletters or companies.\n\n"
                  "Output Format:\n"
                  "Respond strictly in this format: 'Priority: [Priority]'.\n"
                  "Example: 'Priority: 5'.\n\n"
                  "Instructions:\n"
                  "- Do not include any explanations, comments, reasoning, or additional text. write "
                  "number between 1 to 10 only\n"
                  "- Do not write anything other than the format: 'Priority: [Priority]'.\n"
                  "- Violating this format is strictly prohibited.\n"
                  "- Ensure that the output includes only the priority value in the required format and nothing else."

                  )
    elif task == "action":
        prompt = (f"Instructions: \n"
                  f"1. Determine if follow-up action is required for the given email.\n"
                  f"2. If 'noreply' or 'no-reply' appears in the sender or subject, no action is required.\n"
                  f"3. Action is required only if:\n"
                  f"   - The email requests an explicit response or task from you.\n"
                  f"   - The email contains time-sensitive information needing your attention.\n"
                  f"4. Tickets or reports do not require action.\n\n"
                  f"Respond strictly in this format: 'Action Required: [Yes/No]'.\n"
                  f"Do not include any extra words or explanations.\n\n"
                  f"Email Data:\n"
                  f"- Sender: '{sender}'\n"
                  f"- Subject: '{subject}")

    model = GPT4All("Phi-3-mini-4k-instruct.Q4_0.gguf")
    with model.chat_session():

        output = (model.generate(prompt=prompt, max_tokens=100))

        redis_client.setex(request_key, timedelta(hours=4), output)

        return output


def main():
    """
    Main function to authenticate Gmail and fetch emails.
    """
    try:
        # Authenticate with Gmail and get the service object
        service = authenticate_gmail()
        print(f"Fetching 100 emails.")
        # Fetch the latest emails
        emails = get_emails(service, max_results=100)
        mails = []
        categories = {"Work": [],
                      "Shopping": [],
                      "Finance": [],
                      "Health": [],
                      "Tickets": [],
                      "Payment Confirmations": []
                      }
        predefined_categories = list(categories.keys())

        print(f"Fetched {len(emails)} emails.")

        with tqdm(total=len(emails), desc="Processing Emails", unit="email") as pbar:

            for email in emails:
                mail = Email(email['subject'], email['sender'])
                category = interact_with_llm(email['subject'], email['sender'], predefined_categories, "category")
                priority = interact_with_llm(email['subject'], email['sender'], predefined_categories, "priority")
                action = interact_with_llm(email['subject'], email['sender'], predefined_categories, "action")
                mail.category = category.split(":")[1].strip()
                if mail.category in predefined_categories:
                    categories[mail.category].append(mail)
                else:
                    categories[mail.category] = [mail]

                mail.priority = priority.split(":")[1].strip().splitlines()[0]
                mail.action_required = action.split(":")[1].strip() == "Yes"
                mails.append(mail)
                pbar.update(1)

        action_required_mails = sorted(
            [mail for mail in mails if mail.action_required],
            key=lambda x: x.priority,
            reverse=True
        )

        print("\nAction Required Emails (Ordered by Priority):")
        for mail in action_required_mails:
            print(mail)
        print(f"\n num of mails = {len(mails)}")

        category_counts = {category: len(emails) for category, emails in categories.items()}

        print("\nCategory Distribution Pie Chart:")
        labels = list(category_counts.keys())
        sizes = list(category_counts.values())
        plt.figure(figsize=(7, 7))  # Optional: to control figure size
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        plt.title("Distribution of Emails Across Categories")
        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
        plt.show()

        print("\nAction needed Emails Ordered by Priority shown above")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == '__main__':
    main()
