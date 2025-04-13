import os
from pathlib import Path
from dotenv import load_dotenv

class ConfigError(Exception):
    """Custom configuration error"""
    pass

# Load environment variables (but don't validate yet)
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

class BaseConfig:
    """Base configuration with common settings"""
    
    def __init__(self):
        """Initialize and validate configuration"""
        # Security - validate on instance creation, not import
        self.SECRET_KEY = self._get_required_env('SECRET_KEY')
        
        # Application
        self.DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
        
        # Paths
        self.BASE_DIR = Path(__file__).parent.parent
        self.DATABASE_PATH = self.BASE_DIR / 'data' / 'voters.db'
        
        # Blockchain
        self.BLOCKCHAIN_NETWORK = os.getenv('BLOCKCHAIN_NETWORK', 'ganache')
        self.GANACHE_URL = os.getenv('GANACHE_URL', 'http://127.0.0.1:7545')
    
    def _get_required_env(self, var_name):
        """Helper to get required environment variables"""
        value = os.getenv(var_name)
        if not value:
            raise ConfigError(f"{var_name} must be set in environment")
        return value
    
    @property
    def DATABASE_URI(self):
        return f"sqlite:///{self.DATABASE_PATH}"

class DevelopmentConfig(BaseConfig):
    """Development-specific configuration"""
    def __init__(self):
        super().__init__()
        self.DEBUG = True
        self.BLOCKCHAIN_NETWORK = 'ganache'

class ProductionConfig(BaseConfig):
    """Production configuration with tighter security"""
    pass

def get_config(env=None):
    """Factory method for getting appropriate config"""
    env = env or os.getenv('FLASK_ENV', 'development')
    
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig
    }
    
    try:
        return configs[env.lower()]()
    except KeyError:
        raise ConfigError(f"Unknown environment: {env}")