import pytest
from unittest.mock import patch, MagicMock
from email_classifier import classifier

@patch("email_classifier.classifier.get_model")
@patch("email_classifier.classifier.get_cache", return_value=None)
@patch("email_classifier.classifier.set_cache")
def test_interact_with_llm_category(mock_set_cache, mock_get_cache, mock_get_model):
    mock_model = MagicMock()
    mock_model.chat_session.return_value.__enter__.return_value = None
    mock_model.generate.return_value = "Category: Work"
    mock_get_model.return_value = mock_model
    result = classifier.interact_with_llm("subject", "sender", ["Work"], "category")
    assert result == "Category: Work"

@patch("email_classifier.classifier.get_model")
@patch("email_classifier.classifier.get_cache", return_value="Category: Cached")
def test_interact_with_llm_cache(mock_get_cache, mock_get_model):
    result = classifier.interact_with_llm("subject", "sender", ["Work"], "category")
    assert result == "Category: Cached"

@patch("email_classifier.classifier.get_model", side_effect=Exception("LLM error"))
def test_interact_with_llm_llm_error(mock_get_model):
    result = classifier.interact_with_llm("subject", "sender", ["Work"], "category")
    assert result == "" 