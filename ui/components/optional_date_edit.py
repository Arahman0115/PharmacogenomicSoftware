"""Custom optional date picker widget that starts empty"""
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton, QCalendarWidget, QDialog, QVBoxLayout
)
from PyQt6.QtCore import QDate


class OptionalDateEdit(QWidget):
    """Date picker that starts empty and allows optional date selection"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_date = None
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)

        # Display field (editable for typing dates)
        self.date_display = QLineEdit()
        self.date_display.setPlaceholderText("MM/DD/YYYY or click calendar")
        self.date_display.textChanged.connect(self.on_text_changed)
        layout.addWidget(self.date_display)

        # Calendar button
        self.calendar_btn = QPushButton("📅")
        self.calendar_btn.setMaximumWidth(35)
        self.calendar_btn.clicked.connect(self.open_calendar)
        layout.addWidget(self.calendar_btn)

        # Clear button
        self.clear_btn = QPushButton("✕")
        self.clear_btn.setMaximumWidth(35)
        self.clear_btn.clicked.connect(self.clear_date)
        layout.addWidget(self.clear_btn)

    def on_text_changed(self, text):
        """Handle text input - validate and parse date"""
        if not text.strip():
            self.selected_date = None
            return

        # Try to parse the input
        # Accepted formats: MM/DD/YYYY, MM-DD-YYYY, YYYY-MM-DD
        date = None
        for fmt in ["MM/dd/yyyy", "MM-dd-yyyy", "yyyy-MM-dd"]:
            date = QDate.fromString(text.strip(), fmt)
            if date.isValid():
                self.selected_date = date
                return

        # If no valid date was parsed, keep selected_date as previous value
        # (user is still typing)

    def open_calendar(self):
        """Open calendar picker dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Select Date of Birth")
        dialog.setGeometry(100, 100, 350, 300)

        layout = QVBoxLayout(dialog)

        calendar = QCalendarWidget()
        if self.selected_date:
            calendar.setSelectedDate(self.selected_date)
        layout.addWidget(calendar)

        def on_date_selected():
            self.selected_date = calendar.selectedDate()
            # Disconnect text signal to avoid triggering on_text_changed
            self.date_display.textChanged.disconnect()
            self.date_display.setText(self.selected_date.toString("MM/dd/yyyy"))
            self.date_display.textChanged.connect(self.on_text_changed)
            dialog.accept()

        calendar.clicked.connect(on_date_selected)
        dialog.exec()

    def clear_date(self):
        """Clear the selected date"""
        self.selected_date = None
        self.date_display.clear()

    def get_date(self):
        """Get selected date (QDate) or None"""
        return self.selected_date

    def get_date_string(self):
        """Get selected date as string (YYYY-MM-DD) or None"""
        if self.selected_date:
            return self.selected_date.toString("yyyy-MM-dd")
        return None

    def set_date(self, date):
        """Set the date (accepts QDate or string YYYY-MM-DD)"""
        if isinstance(date, str):
            date = QDate.fromString(date, "yyyy-MM-dd")
        if date and date.isValid():
            self.selected_date = date
            self.date_display.setText(date.toString("MM/dd/yyyy"))
