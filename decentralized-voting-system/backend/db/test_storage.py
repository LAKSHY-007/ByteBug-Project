import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.db.block_manage import BlockStorage
from backend.models.block import Block

def test_block_storage():
    print("=== Testing Block Storage ===")
    
    
    storage = BlockStorage(storage_path="backend/db/test_chaindata")
    
    
    test_block = Block(
        index=1,
        transactions=[{"from": "Lakshya", "to": "Pado", "amount": 10}],
        timestamp=1234567890.0,
        previous_hash="0" * 64,
        nonce=100
    )
    try:
        saved_path = storage.save_block(test_block)
        print(f"✓ Block saved to: {saved_path}")
    except Exception as e:
        print(f"✗ Failed to save block: {e}")
        return
    
    try:
        loaded_chain = storage.load_chain()
        if not loaded_chain:
            print("✗ No blocks loaded")
            return
        
        loaded_block = loaded_chain[0]
        print(f"Loaded block with index {loaded_block.index}")
        assert test_block.index == loaded_block.index
        assert test_block.transactions == loaded_block.transactions
        assert test_block.previous_hash == loaded_block.previous_hash
        print("All block data matches")
        
    except Exception as e:
        print(f"Failed to load chain: {e}")
        return
    
    
    print("All tests passed")

if __name__ == "__main__":
    test_block_storage()