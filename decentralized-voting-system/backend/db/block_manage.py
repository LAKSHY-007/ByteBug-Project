import json
import os
from pathlib import Path
from hashlib import sha256
from typing import List, Dict, Optional
from .models import BlockModel, Wallet, BlockMetadata
import logging
from backend.models.block import Block
from backend.db.models import BlockModel
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


logger = logging.getLogger(__name__)

class BlockStorage:
    def __init__(self, storage_path: str = "backend/db/chaindata"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Block storage initialized at {self.storage_path.absolute()}")

    def save_block(self, block: Block) -> Path:
        """Save a block to persistent storage."""
        try:
            block_data = block.to_dict()
            block_path = self.storage_path / f"block_{block.index}.json"
            
            with open(block_path, 'w') as f:
                json.dump(block_data, f, indent=2)
            
            logger.debug(f"Block {block.index} saved to {block_path}")
            return block_path
            
        except (IOError, TypeError) as e:
            logger.error(f"Failed to save block: {e}")
            raise StorageError(f"Failed to save block: {e}")

    def load_chain(self) -> List[Block]:
        """Load all blocks in the chain as Block objects."""
        blocks = []
        try:
            
            block_files = sorted(
                self.storage_path.glob("block_*.json"),
                key=lambda x: int(x.stem.split('_')[1])
            )
            for block_file in block_files:
                try:
                    with open(block_file, 'r') as f:
                        block_data = json.load(f)
                        blocks.append(Block.from_dict(block_data))
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"Invalid block data in {block_file}: {e}")
                    continue
            
            logger.info(f"Loaded {len(blocks)} blocks from chain")
            return blocks
            
        except Exception as e:
            logger.error(f"Failed to load chain: {e}")
            raise StorageError(f"Failed to load chain: {e}")


class StorageError(Exception):
    """Custom storage exceptions"""
    pass