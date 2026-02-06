import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env from project root (next to this config/ directory)
_project_root = Path(__file__).resolve().parent.parent
load_dotenv(_project_root / '.env')


@dataclass
class DatabaseConfig:
    """Centralized database configuration - reads from .env file"""
    HOST: str = os.getenv('DB_HOST', '127.0.0.1')
    PORT: int = int(os.getenv('DB_PORT', '3307'))
    USER: str = os.getenv('DB_USER', '')
    PASSWORD: str = os.getenv('DB_PASSWORD', '')
    DATABASE: str = os.getenv('DB_NAME', '')

    @classmethod
    def get_connection_params(cls):
        """Return connection parameters as dictionary for mysql.connector"""
        if not cls.USER or not cls.DATABASE:
            raise RuntimeError(
                "Database credentials not configured. "
                "Copy .env.example to .env and fill in your values."
            )
        return {
            'host': cls.HOST,
            'port': cls.PORT,
            'user': cls.USER,
            'password': cls.PASSWORD,
            'database': cls.DATABASE
        }
