import os
import pytest

def test_config_env_validation(monkeypatch):
    monkeypatch.setenv("GMAIL_CLIENT_ID", "dummy_id")
    monkeypatch.setenv("GMAIL_CLIENT_SECRET", "dummy_secret")
    import importlib
    import email_classifier.config
    importlib.reload(email_classifier.config)
    assert email_classifier.config.GMAIL_CLIENT_ID == "dummy_id"
    assert email_classifier.config.GMAIL_CLIENT_SECRET == "dummy_secret"


def test_config_missing_env(monkeypatch):
    monkeypatch.delenv("GMAIL_CLIENT_ID", raising=False)
    monkeypatch.delenv("GMAIL_CLIENT_SECRET", raising=False)
    import importlib
    with pytest.raises(RuntimeError):
        import email_classifier.config
        importlib.reload(email_classifier.config) 