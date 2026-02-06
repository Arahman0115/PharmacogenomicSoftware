from PyQt6.QtWidgets import (
    QDialog, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from DataBaseConnection import DatabaseConnection


class PrescriptionDetailView(QDialog):
    def __init__(self, prescriber_info: dict, prescription_id, db_connection, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Prescription Details")
        self.resize(1000, 400)

        self.prescriber_info = prescriber_info
        self.prescription_id = prescription_id
        self.db_connection = db_connection

        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # Left quadrant: Prescriber info
        prescriber_frame = QFrame()
        prescriber_frame.setProperty("cssClass", "card")
        prescriber_layout = QVBoxLayout(prescriber_frame)
        prescriber_layout.setContentsMargins(10, 10, 10, 10)
        prescriber_layout.setSpacing(8)

        title = QLabel("Prescriber Information")
        title.setProperty("cssClass", "section-heading")
        prescriber_layout.addWidget(title)

        fields = [
            ("Medication Name", prescriber_info.get("med_name", "N/A")),
            ("Refills", str(prescriber_info.get("refills", "N/A"))),
            ("Prescriber", prescriber_info.get("prescriber", "N/A")),
            ("Instructions", prescriber_info.get("instructions", "N/A")),
        ]
        for label_text, value in fields:
            label = QLabel(f"<b>{label_text}:</b> {value}")
            label.setWordWrap(True)
            prescriber_layout.addWidget(label)

        prescriber_layout.addStretch()

        # Button to upload image
        self.upload_button = QPushButton("Upload Prescription Image")
        self.upload_button.setProperty("cssClass", "success")
        self.upload_button.clicked.connect(self.upload_image)
        prescriber_layout.addWidget(self.upload_button)

        # Right quadrant: Prescription image or placeholder
        image_frame = QFrame()
        image_frame.setProperty("cssClass", "card")
        image_frame.setFixedSize(480, 320)

        self.image_label = QLabel(image_frame)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setProperty("cssClass", "text-muted")
        self.image_label.setGeometry(0, 0, 480, 320)

        self.load_image_from_data(prescriber_info.get('prescription_image'))

        main_layout.addWidget(prescriber_frame, stretch=1)
        main_layout.addWidget(image_frame, stretch=1)

        close_button = QPushButton("Close")
        close_button.setProperty("cssClass", "ghost")
        close_button.clicked.connect(self.accept)

        wrapper_layout = QVBoxLayout()
        wrapper_layout.addLayout(main_layout)
        wrapper_layout.addWidget(close_button, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(wrapper_layout)

    def load_image_from_data(self, image_data):
        if image_data:
            pixmap = QPixmap()
            pixmap.loadFromData(image_data)
            scaled_pixmap = pixmap.scaled(480, 320, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.setText("Prescription Image\nPlaceholder")

    def upload_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Prescription Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if not file_path:
            return

        pixmap = QPixmap(file_path)
        if pixmap.isNull():
            QMessageBox.warning(self, "Invalid Image", "The selected file is not a valid image.")
            return

        scaled_pixmap = pixmap.scaled(480, 320, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.image_label.setPixmap(scaled_pixmap)

        with open(file_path, 'rb') as f:
            image_bytes = f.read()

        # Create a fresh database connection
        db = DatabaseConnection(
            host='localhost',
            user='pgx_user',
            password="pgx_password",
            database='pgx_db'
        )

        try:
            db.cursor.execute(
                "UPDATE Prescriptions SET prescription_image = %s WHERE prescription_id = %s",
                (image_bytes, self.prescription_id)
            )
            db.connection.commit()
            QMessageBox.information(self, "Success", "Prescription image updated successfully.")
        except Exception as e:
            db.connection.rollback()
            QMessageBox.critical(self, "Database Error", f"Failed to update image in database:\n{e}")
        finally:
            # Clean up the connection
            try:
                db.connection.close()
            except:
                pass
