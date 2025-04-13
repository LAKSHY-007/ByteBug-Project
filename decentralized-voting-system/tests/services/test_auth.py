# tests/services/test_auth.py
import pytest
import numpy as np
from backend.services.auth import BiometricAuthenticator
from backend.core.exceptions import AuthenticationError

class TestBiometricAuthenticator:
    @pytest.fixture
    def authenticator(self):
        return BiometricAuthenticator()
    
    def test_verify_unique_face(self, authenticator):
        
        enc1 = np.random.rand(128)
        enc2 = np.random.rand(128)
        
        
        assert authenticator.verify_unique_face(enc1) is True
        
        
        authenticator.known_voters = {"voter1": enc1}
        
        
        assert authenticator.verify_unique_face(enc1) is False
        
        
        assert authenticator.verify_unique_face(enc2) is True
    
    def test_duplicate_registration(self, authenticator, monkeypatch):
        
        dummy_enc = np.random.rand(128)
        monkeypatch.setattr(
            "backend.services.auth.BiometricAuthenticator.capture_face",
            lambda self: (None, dummy_enc)
        )
        
        
        voter1 = authenticator.register_voter("Lakshya", "voter1")
        
        
        with pytest.raises(AuthenticationError):
            authenticator.register_voter("Pradeep", "voter2")