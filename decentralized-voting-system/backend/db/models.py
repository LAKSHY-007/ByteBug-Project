from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List

class BlockModel(BaseModel):
    index: int
    transactions: List[Dict]
    timestamp: float
    previous_hash: str
    nonce: int
    hash: str

class VoterModel(BaseModel):
    voter_id: str
    face_hash: str
    registered_at: datetime = datetime.now()
    has_voted: bool = False

class Wallet(BaseModel):
    address: str
    public_key: str

    def to_dict(self):
        return {
            "address": self.address,
            "public_key": self.public_key
        }

    @staticmethod
    def from_dict(data: Dict):
        return Wallet(
            address=data["address"],
            public_key=data["public_key"]
        )

class BlockMetadata(BaseModel):
    index: int
    hash: str
    timestamp: float

    def to_dict(self):
        return {
            "index": self.index,
            "hash": self.hash,
            "timestamp": self.timestamp
        }

    @staticmethod
    def from_dict(data: Dict):
        return BlockMetadata(
            index=data["index"],
            hash=data["hash"],
            timestamp=data["timestamp"]
        )
