# backend/core/exceptions.py
class AuthenticationError(Exception):
    """Raised when voter authentication fails"""
    pass

class BlockchainError(Exception):
    """Raised for blockchain-related errors"""
    pass

class DuplicateVoterError(Exception):
    """Raised when duplicate voter is detected"""
    pass