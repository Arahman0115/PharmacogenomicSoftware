import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFontDatabase
from PyQt6.QtCore import Qt
from Login import LoginWindow
from DataBaseConnection import DatabaseConnection
from config import Theme, DatabaseConfig


def load_fonts():
    """Load bundled JetBrains Mono fonts before applying stylesheet."""
    fonts_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
    font_files = [
        "JetBrainsMono-Regular.ttf",
        "JetBrainsMono-Medium.ttf",
        "JetBrainsMono-SemiBold.ttf",
        "JetBrainsMono-Bold.ttf",
    ]
    for font_file in font_files:
        font_path = os.path.join(fonts_dir, font_file)
        if os.path.exists(font_path):
            font_id = QFontDatabase.addApplicationFont(font_path)
            if font_id == -1:
                print(f"Warning: Failed to load font {font_file}")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Load custom fonts first
    load_fonts()

    # Apply unified theme to entire application
    app.setStyleSheet(Theme.get_application_stylesheet())

    # Initialize database connection using centralized configuration
    db_connection = DatabaseConnection(
        host=DatabaseConfig.HOST,
        user=DatabaseConfig.USER,
        password=DatabaseConfig.PASSWORD,
        database=DatabaseConfig.DATABASE,
        port=DatabaseConfig.PORT
    )
    root_login = LoginWindow(db_connection=db_connection)
    root_login.show()
    sys.exit(app.exec())
