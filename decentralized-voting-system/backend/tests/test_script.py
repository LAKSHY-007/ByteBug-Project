from backend.models.block import Block
from datetime import datetime

# Create a test block
test_block = Block(1, [], datetime.now().timestamp(), "0x123")

# Assuming you have storage set up for saving and loading blocks
storage.save_block(test_block)

# Print out the stored chain
print(storage.load_chain())  # Should show your blocks
