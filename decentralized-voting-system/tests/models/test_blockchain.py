
import pytest
from datetime import datetime
from backend.models.block import Block, Blockchain

def test_block_creation():
    block = Block(1, [], datetime.now().timestamp(), "0")
    assert block.index == 1
    assert isinstance(block.compute_hash(), str)

def test_blockchain_initialization():
    bc = Blockchain()
    assert len(bc.chain) == 1 
    assert bc.last_block.index == 0

def test_new_transaction():
    bc = Blockchain()
    idx = bc.new_transaction("sender1", {"name": "Test Voter"})
    assert idx == 1 

def test_proof_of_work():
    bc = Blockchain()
    last_proof = bc.last_block.nonce
    proof = bc.proof_of_work(last_proof)
    assert bc.valid_proof(last_proof, proof)