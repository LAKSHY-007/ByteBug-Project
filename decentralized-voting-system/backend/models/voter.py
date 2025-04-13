# backend/models/voter.py
from typing import Optional
from datetime import datetime
from dataclasses import dataclass, field
import numpy as np
from hashlib import sha256

@dataclass
class Voter:
    voter_id: str
    name: str
    face_encoding: np.ndarray
    fingerprint_hash: str
    registration_date: datetime = field(default_factory=datetime.now)
    has_voted: bool = False
    pin_hash: Optional[str] = field(default=None, init=False, repr=False)
    is_admin: bool = field(default=False, init=False)  # Admin flag

    def __post_init__(self):
        """Validate data after initialization"""
        if not isinstance(self.face_encoding, np.ndarray):
            raise ValueError("Face encoding must be a numpy array")
        if len(self.face_encoding) != 128:
            raise ValueError("Face encoding must be 128-dimensional")

    def set_pin(self, pin: str) -> None:
        if len(pin) != 6 or not pin.isdigit():
            raise ValueError("PIN must be exactly 6 digits")
        self.pin_hash = sha256(pin.encode()).hexdigest()

    def verify_pin(self, pin: str) -> bool:
        if self.pin_hash is None:
            return False
        return sha256(pin.encode()).hexdigest() == self.pin_hash

    def promote_to_admin(self) -> None:
        """Elevate this voter to admin status"""
        self.is_admin = True