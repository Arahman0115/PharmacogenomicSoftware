import mysql
import mysql.connector
from config import DatabaseConfig


class DatabaseConnection:
    def __init__(self, host, user, password, database, port):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port
        )
        self.cursor = self.connection.cursor(dictionary=True)


# Default connection using centralized configuration
db_connection = DatabaseConnection(**DatabaseConfig.get_connection_params())