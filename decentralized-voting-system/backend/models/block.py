import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
from hashlib import sha256

class Block:
    def __init__(self, index: int, transactions: list, timestamp: float, 
                 previous_hash: str, nonce: int = 0, hash: str = None):
        """
        Initialize a Block in the blockchain.
        
        Args:
            index: block ka index
            transactions: List of transactions
            timestamp: Create
            previous_hash: Hash of the previous block
            nonce: The proof-of-work nonce
            hash: Optional pre-computed hash
        """
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = hash if hash else self.compute_hash()

    def compute_hash(self) -> str:
        """Compute the SHA-256 hash of the block's contents."""
        block_string = json.dumps({
            'index': self.index,
            'transactions': self.transactions,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }, sort_keys=True).encode()
        return sha256(block_string).hexdigest()

    def to_dict(self) -> dict:
        """Convert the block to a dictionary for storage."""
        return {
            'index': self.index,
            'transactions': self.transactions,
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce,
            'hash': self.hash
        }

    @classmethod
    def from_dict(cls, block_dict: dict) -> 'Block':
        """Create a Block instance from a dictionary."""
        return cls(
            index=block_dict['index'],
            transactions=block_dict['transactions'],
            timestamp=block_dict['timestamp'],
            previous_hash=block_dict['previous_hash'],
            nonce=block_dict.get('nonce', 0),
            hash=block_dict.get('hash')
        )

class Blockchain:
    def __init__(self, storage_path: str = "db/chaindata"):
        self.chain: List[Block] = []
        self.current_transactions: List[Dict[str, Any]] = []
        self.nodes = set()
        self.difficulty = 4
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._initialize_chain()
    
    def _initialize_chain(self):
        """Load existing chain or create genesis block"""
        chain_files = sorted(self.storage_path.glob("block_*.json"))
        
        if chain_files:
            
            for block_file in chain_files:
                with open(block_file, 'r') as f:
                    block_data = json.load(f)
                    self.chain.append(Block(
                        index=block_data['index'],
                        transactions=block_data['transactions'],
                        timestamp=block_data['timestamp'],
                        previous_hash=block_data['previous_hash'],
                        nonce=block_data['nonce']
                    ))
        else:
            self.create_genesis_block()
    
    def create_genesis_block(self):
        """Creates and persists the first block"""
        genesis_block = Block(
            index=0,
            transactions=[],
            timestamp=datetime.now().timestamp(),
            previous_hash="0"
        )
        self._persist_block(genesis_block)
        self.chain.append(genesis_block)
    
    def _persist_block(self, block: Block):
        """Save block to disk"""
        block_path = self.storage_path / f"block_{block.index}.json"
        with open(block_path, 'w') as f:
            json.dump(block.to_dict(), f, indent=2)
    
    @property
    def last_block(self) -> Block:
        return self.chain[-1]
    
    def new_block(self, proof: int) -> Block:
        """Creates, persists, and returns new block"""
        block = Block(
            index=len(self.chain),
            transactions=self.current_transactions,
            timestamp=datetime.now().timestamp(),
            previous_hash=self.last_block.hash,
            nonce=proof
        )
        
        self.current_transactions = []
        self._persist_block(block)
        self.chain.append(block)
        return block
    
    def new_transaction(self, sender: str, voter_data: Dict[str, Any]) -> int:
        """Adds transaction with enhanced data structure"""
        tx = {
            'sender': sender,
            'voter_data': voter_data,
            'timestamp': datetime.now().timestamp(),
            'tx_hash': hashlib.sha256(
                json.dumps(voter_data, sort_keys=True).encode()
            ).hexdigest()
        }
        self.current_transactions.append(tx)
        return self.last_block.index + 1
    
    def proof_of_work(self, last_block: Block) -> int:
        """Improved PoW using last block's hash"""
        last_hash = last_block.hash
        proof = 0
        while not self.valid_proof(last_hash, proof):
            proof += 1
        return proof
    
    def valid_proof(self, last_hash: str, proof: int) -> bool:
        """Validates proof against chain difficulty"""
        guess = f'{last_hash}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:self.difficulty] == '0' * self.difficulty
    
    def validate_chain(self) -> bool:
        """Verify blockchain integrity"""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            
            
            if current.hash != current.compute_hash():
                return False
                
            
            if current.previous_hash != previous.hash:
                return False
        return True

    def get_block(self, index: int) -> Optional[Block]:
        """Retrieve block by index"""
        try:
            return self.chain[index]
        except IndexError:
            return None