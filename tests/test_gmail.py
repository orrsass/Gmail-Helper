import pytest
from unittest.mock import patch, MagicMock
from email_classifier import gmail

@patch("email_classifier.gmail.build")
@patch("email_classifier.gmail.pickle.load")
@patch("email_classifier.gmail.os.path.exists", return_value=False)
def test_authenticate_gmail_new_token(mock_exists, mock_pickle, mock_build):
    with patch("email_classifier.gmail.InstalledAppFlow.from_client_secrets_file") as mock_flow:
        mock_flow.return_value.run_local_server.return_value = MagicMock()
        service = gmail.authenticate_gmail()
        assert mock_build.called

@patch("email_classifier.gmail.build")
@patch("email_classifier.gmail.pickle.load")
@patch("email_classifier.gmail.os.path.exists", return_value=True)
def test_authenticate_gmail_existing_token(mock_exists, mock_pickle, mock_build):
    mock_pickle.return_value = MagicMock(valid=True)
    service = gmail.authenticate_gmail()
    assert mock_build.called

@patch("email_classifier.gmail.Resource")
def test_get_emails_success(mock_resource):
    service = MagicMock()
    service.users().messages().list().execute.return_value = {"messages": [{"id": "1"}]}
    service.users().messages().get().execute.return_value = {"payload": {"headers": [{"name": "Subject", "value": "Test"}, {"name": "From", "value": "test@example.com"}]}}
    emails = gmail.get_emails(service, max_results=1)
    assert emails == [{"subject": "Test", "sender": "test@example.com"}]

@patch("email_classifier.gmail.Resource")
def test_get_emails_error(mock_resource):
    service = MagicMock()
    service.users().messages().list().execute.side_effect = Exception("API error")
    emails = gmail.get_emails(service, max_results=1)
    assert emails == [] 