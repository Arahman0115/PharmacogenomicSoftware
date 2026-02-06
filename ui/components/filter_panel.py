from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDateEdit, QPushButton, QFrame
from PyQt6.QtCore import pyqtSignal
from config import Theme


class FilterPanel(QWidget):
    """Reusable filter panel for queue views

    Eliminates duplication between Reception.py and ProductSelectionView.py
    """

    filters_changed = pyqtSignal(dict)  # Emits filter values

    def __init__(self, parent=None, filters_config=None):
        super().__init__(parent)
        self.filters_config = filters_config or {}
        self.filter_widgets = {}
        self.init_ui()

    def init_ui(self):
        frame = QFrame()
        frame.setProperty("cssClass", "filter-panel")

        layout = QVBoxLayout(frame)
        layout.setContentsMargins(
            Theme.MARGIN_NORMAL, Theme.MARGIN_NORMAL,
            Theme.MARGIN_NORMAL, Theme.MARGIN_NORMAL
        )
        layout.setSpacing(Theme.SPACING_NORMAL)

        # Build filter rows based on configuration
        for filter_name, filter_config in self.filters_config.items():
            self.add_filter_row(layout, filter_name, filter_config)

        # Filter and Reset buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        filter_btn = QPushButton("Filter")
        filter_btn.setProperty("cssClass", "primary")
        filter_btn.clicked.connect(self.apply_filters)
        button_layout.addWidget(filter_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.setProperty("cssClass", "ghost")
        reset_btn.clicked.connect(self.reset_filters)
        button_layout.addWidget(reset_btn)

        layout.addLayout(button_layout)

        main_layout = QVBoxLayout(self)
        main_layout.addWidget(frame)
        main_layout.setContentsMargins(0, 0, 0, 0)

    def add_filter_row(self, layout, name, config):
        """Add a filter widget based on configuration"""
        row_layout = QHBoxLayout()

        label = QLabel(config.get('label', name))
        row_layout.addWidget(label)

        filter_type = config.get('type', 'text')
        if filter_type == 'text':
            widget = QLineEdit()
        elif filter_type == 'date':
            widget = QDateEdit()
            widget.setCalendarPopup(True)
        else:
            widget = QLineEdit()

        self.filter_widgets[name] = widget
        row_layout.addWidget(widget)
        row_layout.addStretch()

        layout.addLayout(row_layout)

    def apply_filters(self):
        """Collect filter values and emit signal"""
        filters = {}
        for name, widget in self.filter_widgets.items():
            if isinstance(widget, QDateEdit):
                filters[name] = widget.date().toString("yyyy-MM-dd")
            else:
                filters[name] = widget.text()
        self.filters_changed.emit(filters)

    def reset_filters(self):
        """Clear all filters"""
        for widget in self.filter_widgets.values():
            if isinstance(widget, QLineEdit):
                widget.clear()
            elif isinstance(widget, QDateEdit):
                widget.setDate(widget.date())
        # Emit empty filters
        self.filters_changed.emit({})

    def get_filters(self):
        """Get current filter values without emitting signal"""
        filters = {}
        for name, widget in self.filter_widgets.items():
            if isinstance(widget, QDateEdit):
                filters[name] = widget.date().toString("yyyy-MM-dd")
            else:
                filters[name] = widget.text()
        return filters
