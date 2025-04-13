from .block_manage import BlockStorage, VoterStorage

def initialize():
    BlockStorage().storage_path.mkdir(exist_ok=True)
    VoterStorage().storage_path.mkdir(exist_ok=True)
    print("Database initialized successfully")

if __name__ == "__main__":
    initialize()