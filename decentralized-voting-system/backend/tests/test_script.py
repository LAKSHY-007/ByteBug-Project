from backend.models.block import Block
from datetime import datetime

test_block = Block(1, [], datetime.now().timestamp(), "0x123")


storage.save_block(test_block)


print(storage.load_chain())  
