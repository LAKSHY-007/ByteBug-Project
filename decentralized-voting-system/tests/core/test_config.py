import os
import sys
import pytest
import importlib
from unittest.mock import patch
from backend.core.config import BaseConfig, DevelopmentConfig, ProductionConfig, get_config, ConfigError

def test_dev_config():
    """Test development configuration"""
    with patch.dict(os.environ, {'SECRET_KEY': 'test-key'}):
        cfg = get_config('development')
        assert cfg.DEBUG is True
        assert cfg.BLOCKCHAIN_NETWORK == 'ganache'

def test_prod_config():
    """Test production configuration"""
    with patch.dict(os.environ, {'SECRET_KEY': 'test-key'}):
        cfg = get_config('production')
        assert cfg.DEBUG is False

def test_missing_key():
    """Test missing SECRET_KEY raises ConfigError"""
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(ConfigError, match="SECRET_KEY must be set"):
            get_config('development')

def test_invalid_environment():
    """Test invalid environment raises ConfigError"""
    with patch.dict(os.environ, {'SECRET_KEY': 'test-key'}):
        with pytest.raises(ConfigError, match="Unknown environment"):
            get_config('invalid_env')
