from email_classifier.models import Email

def test_email_defaults():
    email = Email(subject="Test", sender="test@example.com")
    assert email.subject == "Test"
    assert email.sender == "test@example.com"
    assert email.category is None
    assert email.priority is None
    assert email.action_required is False

def test_email_fields():
    email = Email(subject="Hello", sender="a@b.com", category="Work", priority=5, action_required=True)
    assert email.category == "Work"
    assert email.priority == 5
    assert email.action_required is True 