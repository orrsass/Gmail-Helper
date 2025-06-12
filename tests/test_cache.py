from email_classifier import cache
from unittest.mock import patch, MagicMock

def test_get_cache_success():
    with patch.object(cache.redis_client, 'get', return_value='value'):
        assert cache.get_cache('key') == 'value'

def test_get_cache_error():
    with patch.object(cache.redis_client, 'get', side_effect=Exception()):
        assert cache.get_cache('key') is None

def test_set_cache_success():
    with patch.object(cache.redis_client, 'setex', return_value=True):
        assert cache.set_cache('key', 'value', ex=10) is None

def test_set_cache_error():
    with patch.object(cache.redis_client, 'setex', side_effect=Exception()):
        assert cache.set_cache('key', 'value', ex=10) is None 