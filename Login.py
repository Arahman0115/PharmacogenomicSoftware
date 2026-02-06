from PyQt6 import QtWidgets, QtGui, QtCore
from mainwindow import MainWindow
from DataBaseConnection import DatabaseConnection
from config import DatabaseConfig
import sys
import mysql.connector


class LoginWindow(QtWidgets.QWidget):
    def __init__(self, db_connection):
        super().__init__()

        self.setWindowTitle("Nexus Controls - Login")
        self.setFixedSize(750, 500)

        # Center window
        qr = self.frameGeometry()
        screen = QtWidgets.QApplication.primaryScreen()
        rect = screen.availableGeometry()
        center_point = rect.center()
        qr.moveCenter(center_point)
        self.move(qr.topLeft())

        # Use the provided database connection
        self.db_connection = db_connection

        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # Title
        title_label = QtWidgets.QLabel("Pharmacogenomic Systems")
        title_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        title_label.setProperty("cssClass", "page-title")
        layout.addWidget(title_label)

        layout.addSpacing(20)

        # Images
        try:
            pillori_pixmap = QtGui.QPixmap("PNGS/pillbottlesblurgrey.png").scaled(
                750, 300,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation
            )
            pillori_label = QtWidgets.QLabel()
            pillori_label.setPixmap(pillori_pixmap)
            pillori_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(pillori_label)
        except Exception as e:
            print(f"Image loading failed: {e}")

        # Form
        form_layout = QtWidgets.QFormLayout()
        layout.addLayout(form_layout)

        self.username_edit = QtWidgets.QLineEdit()
        self.password_edit = QtWidgets.QLineEdit()
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        form_layout.addRow("Username:", self.username_edit)
        form_layout.addRow("Password:", self.password_edit)

        info_label = QtWidgets.QLabel("Enter your Username and Password to log in")
        info_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        info_label.setProperty("cssClass", "text-muted")
        layout.addWidget(info_label)

        # Login button - primary-large style
        self.login_button = QtWidgets.QPushButton("Login")
        self.login_button.setProperty("cssClass", "primary-large")
        self.login_button.clicked.connect(self.correct_login)
        self.login_button.setCursor(QtGui.QCursor(QtCore.Qt.CursorShape.PointingHandCursor))
        layout.addWidget(self.login_button)

        # Error label
        self.error_label = QtWidgets.QLabel("")
        self.error_label.setProperty("cssClass", "error-text")
        self.error_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.error_label)

    def correct_login(self):
        if not self.db_connection or not self.db_connection.connection.is_connected():
            self.error_label.setText("No database connection available")
            return

        username = self.username_edit.text()
        password = self.password_edit.text()

        try:
            cursor = self.db_connection.connection.cursor(dictionary=True)
            cursor.execute(
                'SELECT Username, Password FROM UserEntry WHERE Username = %s AND Password = %s',
                (username, password)
            )
            result = cursor.fetchone()
            cursor.close()  # close the cursor, keep connection alive

            if result:
                self.error_label.setText("")
                # Pass the same db_connection to MainWindow
                self.main_window = MainWindow(db_connection=self.db_connection)
                self.main_window.show()
                self.close()
            else:
                self.error_label.setText("Incorrect Username/Password")

        except mysql.connector.Error as err:
            self.error_label.setText(f"Database error: {err}")


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    # Create single database connection instance using centralized config
    db_connection = DatabaseConnection(
        host=DatabaseConfig.HOST,
        user=DatabaseConfig.USER,
        password=DatabaseConfig.PASSWORD,
        database=DatabaseConfig.DATABASE,
        port=DatabaseConfig.PORT
    )

    login = LoginWindow(db_connection=db_connection)
    login.show()
    sys.exit(app.exec())
