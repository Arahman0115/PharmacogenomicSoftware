import os
from dataclasses import dataclass


@dataclass
class DatabaseConfig:
    """Centralized database configuration with environment variable support"""
    HOST: str = os.getenv('DB_HOST', '127.0.0.1')
    PORT: int = int(os.getenv('DB_PORT', '3307'))
    USER: str = os.getenv('DB_USER', 'pgx_user')
    PASSWORD: str = os.getenv('DB_PASSWORD', 'Auddin')
    DATABASE: str = os.getenv('DB_NAME', 'pgx_db')

    @classmethod
    def get_connection_params(cls):
        """Return connection parameters as dictionary for mysql.connector"""
        return {
            'host': cls.HOST,
            'port': cls.PORT,
            'user': cls.USER,
            'password': cls.PASSWORD,
            'database': cls.DATABASE
        }
