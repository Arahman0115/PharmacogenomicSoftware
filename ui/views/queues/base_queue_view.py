from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
    QTableWidgetItem, QFrame, QHeaderView, QLabel
)
from PyQt6.QtCore import Qt
from config import Theme
from ui.components.card_row_delegate import CardRowDelegate


class BaseQueueView(QWidget):
    """Base class for all queue views

    Consolidates duplicate code from Reception.py and ProductSelectionView.py
    Subclasses override these properties:
    - TABLE_NAME: Database table name to query
    - WINDOW_TITLE: Display title
    - FILTERS_CONFIG: Filter panel configuration
    - COLUMNS: Table column headers
    - QUERY: SQL query template
    """

    # Subclasses must override these
    TABLE_NAME = None
    WINDOW_TITLE = "Queue View"
    FILTERS_CONFIG = {}
    COLUMNS = []       # Display header labels
    COLUMN_KEYS = []   # Corresponding database column keys (must match COLUMNS length)
    QUERY = None

    def __init__(self, db_connection, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.current_page = 0
        self.page_size = 50
        self.total_records = 0
        self.current_filters = {}
        self.current_data = []

        self.setWindowTitle(self.WINDOW_TITLE)
        self.setMinimumSize(1000, 700)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            Theme.MARGIN_NORMAL, Theme.MARGIN_NORMAL,
            Theme.MARGIN_NORMAL, Theme.MARGIN_NORMAL
        )
        layout.setSpacing(Theme.SPACING_NORMAL)

        # Queue title label
        title_label = QLabel(self.WINDOW_TITLE)
        title_label.setStyleSheet(f"""
            color: {Theme.TEXT_PRIMARY};
            font-size: 18px;
            font-weight: bold;
            padding: 6px 0px;
        """)
        layout.addWidget(title_label)

        # Filter section - uses cssClass property for global theme
        self.filter_frame = QFrame()
        self.filter_frame.setProperty("cssClass", "filter-panel")
        filter_layout = QVBoxLayout(self.filter_frame)
        self.create_filters(filter_layout)
        layout.addWidget(self.filter_frame)

        # Table
        self.table = self.create_table()
        layout.addWidget(self.table)

        # Bottom section (pagination + buttons)
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()

        self.page_up_btn = QPushButton("Page Up")
        self.page_up_btn.setProperty("cssClass", "ghost")
        self.page_up_btn.clicked.connect(self.previous_page)
        bottom_layout.addWidget(self.page_up_btn)

        self.page_down_btn = QPushButton("Page Down")
        self.page_down_btn.setProperty("cssClass", "ghost")
        self.page_down_btn.clicked.connect(self.next_page)
        bottom_layout.addWidget(self.page_down_btn)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setProperty("cssClass", "secondary")
        self.refresh_btn.clicked.connect(self.refresh)
        bottom_layout.addWidget(self.refresh_btn)

        close_btn = QPushButton("Close")
        close_btn.setProperty("cssClass", "ghost")
        close_btn.clicked.connect(self.close)
        bottom_layout.addWidget(close_btn)

        layout.addLayout(bottom_layout)

    def create_filters(self, parent_layout):
        """Create filter controls - subclasses can override"""
        pass

    def create_table(self):
        """Create and configure the table widget with card-style rows"""
        table = QTableWidget()
        table.setColumnCount(len(self.COLUMNS))
        table.setHorizontalHeaderLabels(self.COLUMNS)
        table.setShowGrid(False)
        table.setAlternatingRowColors(False)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.itemDoubleClicked.connect(self.on_row_double_clicked)

        # Set row height for card-style spacing
        table.verticalHeader().setDefaultSectionSize(Theme.TABLE_ROW_HEIGHT)
        table.verticalHeader().setVisible(False)

        # Set header styling
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setHighlightSections(False)

        # Enable mouse tracking for hover effects
        table.setMouseTracking(True)

        # Optional: wire CardRowDelegate for enhanced rendering
        delegate = CardRowDelegate(table)
        table.setItemDelegate(delegate)

        return table

    def load_data(self):
        """Load data from database - subclasses override"""
        raise NotImplementedError(f"{self.__class__.__name__} must implement load_data()")

    def display_data(self, data):
        """Display data in table"""
        self.table.setRowCount(len(data))
        keys = self.COLUMN_KEYS if self.COLUMN_KEYS else self.COLUMNS

        for row, record in enumerate(data):
            for col, key in enumerate(keys):
                value = record.get(key, "")
                item = QTableWidgetItem(str(value) if value is not None else "")
                item.setData(256, record)
                self.table.setItem(row, col, item)

    def on_row_double_clicked(self, item):
        """Handle row double-click - subclasses can override"""
        pass

    def apply_filters(self, filters):
        """Apply filters and reload data"""
        self.current_filters = filters
        self.current_page = 0
        self.load_data()

    def refresh(self):
        """Refresh current page data"""
        self.load_data()

    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.load_data()

    def next_page(self):
        """Go to next page"""
        max_pages = (self.total_records + self.page_size - 1) // self.page_size
        if self.current_page < max_pages - 1:
            self.current_page += 1
            self.load_data()

    def get_selected_row_data(self):
        """Get data from selected row"""
        selected_rows = self.table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            item = self.table.item(row, 0)
            return item.data(256)
        return None

    def get_offset(self):
        """Calculate database query offset"""
        return self.current_page * self.page_size
