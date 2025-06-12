import click
import logging
from collections import defaultdict
from email_classifier.gmail import authenticate_gmail, get_emails
from email_classifier.classifier import interact_with_llm
from email_classifier.plotter import plot_category_distribution
from email_classifier.models import Email
from tqdm import tqdm
from typing import List
import sys

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

@click.group()
def cli():
    """Email Classifier CLI"""
    pass

def fetch_emails() -> List[Email]:
    service = authenticate_gmail()
    emails = get_emails(service, max_results=100)
    return [Email(email['subject'], email['sender']) for email in emails]

@cli.command()
def fetch():
    """Fetch emails from Gmail."""
    emails = fetch_emails()
    log.info(f"Fetched {len(emails)} emails.")

@cli.command()
def classify():
    """Classify fetched emails."""
    emails = fetch_emails()
    predefined_categories = ["Work", "Shopping", "Finance", "Health", "Tickets", "Payment Confirmations"]
    categories = defaultdict(list)
    mails = []
    with tqdm(total=len(emails), desc="Processing Emails", unit="email") as pbar:
        for email in emails:
            category = interact_with_llm(email.subject, email.sender, predefined_categories, "category")
            priority = interact_with_llm(email.subject, email.sender, predefined_categories, "priority")
            action = interact_with_llm(email.subject, email.sender, predefined_categories, "action")
            email.category = category
            email.priority = int(priority) if priority.isdigit() else None
            email.action_required = action.lower() == "yes"
            categories[email.category].append(email)
            mails.append(email)
            pbar.update(1)
    action_required_mails = sorted(
        [mail for mail in mails if mail.action_required],
        key=lambda x: x.priority if x.priority is not None else 0,
        reverse=True
    )
    log.info("\nAction Required Emails (Ordered by Priority):")
    for mail in action_required_mails:
        log.info(mail)
    log.info(f"\n num of mails = {len(mails)}")

@cli.command()
@click.option('--save-path', default=None, help='Path to save the plot if not interactive.')
def plot(save_path):
    """Plot classification results."""
    emails = fetch_emails()
    predefined_categories = ["Work", "Shopping", "Finance", "Health", "Tickets", "Payment Confirmations"]
    categories = defaultdict(list)
    for email in emails:
        category = interact_with_llm(email.subject, email.sender, predefined_categories, "category")
        email.category = category
        categories[email.category].append(email)
    category_counts = {category: len(emails) for category, emails in categories.items()}
    fig = plot_category_distribution(category_counts, save_path=save_path)
    if not save_path:
        import matplotlib.pyplot as plt
        plt.show()

if __name__ == "__main__":
    sys.exit(cli()) 