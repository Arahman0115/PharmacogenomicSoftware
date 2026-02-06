class Theme:
    """Modern design system for the Pharmacogenomic Software application.

    Single source of truth for all colors, typography, spacing, and QSS styles.
    No file should use inline setStyleSheet() for theming - everything flows from here.
    """

    # ── Color Palette: "Cool Slate" ──────────────────────────────────────

    # Backgrounds
    BACKGROUND_PRIMARY = "#1E2128"      # Dark slate (main bg)
    BACKGROUND_SECONDARY = "#262A33"    # Slightly lighter (panels, filters)
    SURFACE = "#2C313A"                 # Card surfaces
    SURFACE_HOVER = "#333842"           # Subtle hover tint

    # Accent Primary (Bright Blue for dark bg)
    ACCENT_PRIMARY = "#4A90D9"          # Primary buttons, active states
    ACCENT_PRIMARY_HOVER = "#3A7BC8"    # Darker blue hover
    ACCENT_PRIMARY_LIGHT = "#2A3A50"    # Selection backgrounds, badges

    # Accent Secondary (Amber)
    ACCENT_SECONDARY = "#D97706"        # Secondary highlights, warnings
    ACCENT_SECONDARY_LIGHT = "#3D3020"  # Warning backgrounds

    # Text
    TEXT_PRIMARY = "#D4D7DD"            # Light gray text
    TEXT_SECONDARY = "#8B919A"          # Medium gray
    TEXT_MUTED = "#555B66"              # Placeholders, disabled
    TEXT_INVERSE = "#FFFFFF"            # Text on dark backgrounds

    # Borders
    BORDER_DEFAULT = "#3A3F4A"          # Slate borders
    BORDER_LIGHT = "#2F343D"            # Subtle dividers
    BORDER_FOCUS = "#4A90D9"            # Blue focus ring

    # Navigation
    NAV_BACKGROUND = "#13151A"          # Darkest nav bar
    NAV_TEXT = "#C8CCD4"                # Light nav text

    # Status Colors
    SUCCESS = "#38A169"
    SUCCESS_HOVER = "#2F855A"
    SUCCESS_LIGHT = "#1A2E22"
    ERROR = "#E53E3E"
    ERROR_HOVER = "#C53030"
    ERROR_LIGHT = "#2E1A1A"
    WARNING = "#D97706"
    WARNING_HOVER = "#B45309"
    WARNING_LIGHT = "#2E2510"
    INFO = "#4A90D9"

    # Legacy aliases (for code that still references old names)
    BORDER_COLOR = BORDER_DEFAULT
    SELECTION_COLOR = ACCENT_PRIMARY
    ERROR_COLOR = ERROR
    WARNING_COLOR = WARNING
    SUCCESS_COLOR = SUCCESS
    INFO_COLOR = INFO

    # ── Typography ──────────────────────────────────────────────────────────

    FONT_FAMILY = "'JetBrains Mono', 'Fira Code', 'Cascadia Code', 'Consolas', monospace"
    FONT_SIZE_BADGE = "8px"
    FONT_SIZE_SMALL = "9px"
    FONT_SIZE_NORMAL = "10.5px"
    FONT_SIZE_LABEL = "12px"
    FONT_SIZE_LARGE = "12px"
    FONT_SIZE_HEADER = "14px"
    FONT_SIZE_TITLE = "17px"
    FONT_SIZE_LOGIN_TITLE = "21px"

    # ── Spacing ─────────────────────────────────────────────────────────────

    MARGIN_SMALL = 3
    MARGIN_NORMAL = 6
    MARGIN_LARGE = 14
    SPACING_SMALL = 3
    SPACING_NORMAL = 6
    SPACING_LARGE = 10

    # ── Dimensions ──────────────────────────────────────────────────────────

    TABLE_ROW_HEIGHT = 36
    BUTTON_HEIGHT_SMALL = 22
    BUTTON_HEIGHT_MEDIUM = 28
    BUTTON_HEIGHT_LARGE = 34
    BORDER_RADIUS_PILL = "9999px"
    BORDER_RADIUS_CARD = "6px"
    BORDER_RADIUS_INPUT = "4px"

    @staticmethod
    def get_application_stylesheet():
        """Master stylesheet for entire application.

        Covers every widget type with the modern cool-slate dark theme.
        Button variants are selected via: button.setProperty("cssClass", "primary")
        """
        T = Theme
        return f"""
            /* ═══════════════════════════════════════════
               BASE WIDGET
               ═══════════════════════════════════════════ */
            QWidget {{
                background-color: {T.BACKGROUND_PRIMARY};
                color: {T.TEXT_PRIMARY};
                font-family: {T.FONT_FAMILY};
                font-size: {T.FONT_SIZE_NORMAL};
            }}

            QMainWindow {{
                background-color: {T.BACKGROUND_PRIMARY};
            }}

            QDialog {{
                background-color: {T.BACKGROUND_PRIMARY};
            }}

            /* ═══════════════════════════════════════════
               LABELS
               ═══════════════════════════════════════════ */
            QLabel {{
                color: {T.TEXT_PRIMARY};
                background-color: transparent;
            }}

            QLabel[cssClass="page-title"] {{
                font-size: {T.FONT_SIZE_TITLE};
                font-weight: 700;
                color: {T.TEXT_PRIMARY};
                padding: 4px 0px;
            }}

            QLabel[cssClass="section-heading"] {{
                font-size: {T.FONT_SIZE_HEADER};
                font-weight: 600;
                color: {T.TEXT_PRIMARY};
                padding: 2px 0px;
            }}

            QLabel[cssClass="highlight-label"] {{
                background-color: {T.ACCENT_PRIMARY_LIGHT};
                color: {T.ACCENT_PRIMARY};
                padding: 4px 8px;
                border-radius: {T.BORDER_RADIUS_CARD};
                font-weight: 600;
                font-size: {T.FONT_SIZE_LABEL};
            }}

            QLabel[cssClass="badge-success"] {{
                background-color: {T.SUCCESS_LIGHT};
                color: {T.SUCCESS};
                padding: 2px 6px;
                border-radius: 10px;
                font-size: {T.FONT_SIZE_BADGE};
                font-weight: 600;
            }}

            QLabel[cssClass="badge-warning"] {{
                background-color: {T.WARNING_LIGHT};
                color: {T.WARNING};
                padding: 2px 6px;
                border-radius: 10px;
                font-size: {T.FONT_SIZE_BADGE};
                font-weight: 600;
            }}

            QLabel[cssClass="badge-error"] {{
                background-color: {T.ERROR_LIGHT};
                color: {T.ERROR};
                padding: 2px 6px;
                border-radius: 10px;
                font-size: {T.FONT_SIZE_BADGE};
                font-weight: 600;
            }}

            QLabel[cssClass="badge-info"] {{
                background-color: {T.ACCENT_PRIMARY_LIGHT};
                color: {T.INFO};
                padding: 2px 6px;
                border-radius: 10px;
                font-size: {T.FONT_SIZE_BADGE};
                font-weight: 600;
            }}

            QLabel[cssClass="text-muted"] {{
                color: {T.TEXT_MUTED};
                font-size: {T.FONT_SIZE_SMALL};
            }}

            QLabel[cssClass="text-secondary"] {{
                color: {T.TEXT_SECONDARY};
            }}

            QLabel[cssClass="error-text"] {{
                color: {T.ERROR};
                font-weight: 600;
            }}

            /* ═══════════════════════════════════════════
               BUTTONS - Default (unstyled fallback)
               ═══════════════════════════════════════════ */
            QPushButton {{
                background-color: {T.BACKGROUND_SECONDARY};
                color: {T.TEXT_PRIMARY};
                border: 1px solid {T.BORDER_DEFAULT};
                padding: 4px 12px;
                border-radius: {T.BORDER_RADIUS_PILL};
                font-weight: 600;
                font-size: {T.FONT_SIZE_LABEL};
                min-height: {T.BUTTON_HEIGHT_MEDIUM}px;
            }}

            QPushButton:hover {{
                background-color: {T.SURFACE_HOVER};
                border-color: {T.ACCENT_PRIMARY};
            }}

            QPushButton:pressed {{
                background-color: {T.ACCENT_PRIMARY_LIGHT};
            }}

            QPushButton:disabled {{
                background-color: {T.BACKGROUND_SECONDARY};
                color: {T.TEXT_MUTED};
                border-color: {T.BORDER_LIGHT};
            }}

            /* ── Primary (Bright Blue) ─────────────────── */
            QPushButton[cssClass="primary"] {{
                background-color: {T.ACCENT_PRIMARY};
                color: {T.TEXT_INVERSE};
                border: none;
                padding: 4px 16px;
                border-radius: {T.BORDER_RADIUS_PILL};
                font-weight: 600;
                min-height: {T.BUTTON_HEIGHT_MEDIUM}px;
            }}

            QPushButton[cssClass="primary"]:hover {{
                background-color: {T.ACCENT_PRIMARY_HOVER};
            }}

            QPushButton[cssClass="primary"]:pressed {{
                background-color: #1A3050;
            }}

            QPushButton[cssClass="primary"]:disabled {{
                background-color: {T.TEXT_MUTED};
                color: {T.BACKGROUND_SECONDARY};
            }}

            /* ── Primary Large ────────────────────────── */
            QPushButton[cssClass="primary-large"] {{
                background-color: {T.ACCENT_PRIMARY};
                color: {T.TEXT_INVERSE};
                border: none;
                padding: 6px 24px;
                border-radius: {T.BORDER_RADIUS_PILL};
                font-weight: 700;
                font-size: {T.FONT_SIZE_HEADER};
                min-height: {T.BUTTON_HEIGHT_LARGE}px;
            }}

            QPushButton[cssClass="primary-large"]:hover {{
                background-color: {T.ACCENT_PRIMARY_HOVER};
            }}

            QPushButton[cssClass="primary-large"]:pressed {{
                background-color: #1A3050;
            }}

            /* ── Secondary (Blue Outline) ─────────────── */
            QPushButton[cssClass="secondary"] {{
                background-color: transparent;
                color: {T.ACCENT_PRIMARY};
                border: 2px solid {T.ACCENT_PRIMARY};
                padding: 4px 12px;
                border-radius: {T.BORDER_RADIUS_PILL};
                font-weight: 600;
                min-height: {T.BUTTON_HEIGHT_MEDIUM}px;
            }}

            QPushButton[cssClass="secondary"]:hover {{
                background-color: {T.ACCENT_PRIMARY_LIGHT};
            }}

            QPushButton[cssClass="secondary"]:pressed {{
                background-color: {T.ACCENT_PRIMARY};
                color: {T.TEXT_INVERSE};
            }}

            /* ── Ghost (Slate Border, Gray Text) ──────── */
            QPushButton[cssClass="ghost"] {{
                background-color: transparent;
                color: {T.TEXT_SECONDARY};
                border: 1px solid {T.BORDER_DEFAULT};
                padding: 4px 12px;
                border-radius: {T.BORDER_RADIUS_PILL};
                font-weight: 500;
                min-height: {T.BUTTON_HEIGHT_MEDIUM}px;
            }}

            QPushButton[cssClass="ghost"]:hover {{
                background-color: {T.BACKGROUND_SECONDARY};
                color: {T.TEXT_PRIMARY};
                border-color: {T.TEXT_SECONDARY};
            }}

            QPushButton[cssClass="ghost"]:pressed {{
                background-color: {T.BORDER_LIGHT};
            }}

            /* ── Success (Green) ──────────────────────── */
            QPushButton[cssClass="success"] {{
                background-color: {T.SUCCESS};
                color: {T.TEXT_INVERSE};
                border: none;
                padding: 4px 16px;
                border-radius: {T.BORDER_RADIUS_PILL};
                font-weight: 600;
                min-height: {T.BUTTON_HEIGHT_MEDIUM}px;
            }}

            QPushButton[cssClass="success"]:hover {{
                background-color: {T.SUCCESS_HOVER};
            }}

            QPushButton[cssClass="success"]:pressed {{
                background-color: #276749;
            }}

            /* ── Danger (Red) ─────────────────────────── */
            QPushButton[cssClass="danger"] {{
                background-color: {T.ERROR};
                color: {T.TEXT_INVERSE};
                border: none;
                padding: 4px 16px;
                border-radius: {T.BORDER_RADIUS_PILL};
                font-weight: 600;
                min-height: {T.BUTTON_HEIGHT_MEDIUM}px;
            }}

            QPushButton[cssClass="danger"]:hover {{
                background-color: {T.ERROR_HOVER};
            }}

            QPushButton[cssClass="danger"]:pressed {{
                background-color: #9B2C2C;
            }}

            /* ── Warning (Amber) ──────────────────────── */
            QPushButton[cssClass="warning"] {{
                background-color: {T.WARNING};
                color: {T.TEXT_INVERSE};
                border: none;
                padding: 4px 16px;
                border-radius: {T.BORDER_RADIUS_PILL};
                font-weight: 600;
                min-height: {T.BUTTON_HEIGHT_MEDIUM}px;
            }}

            QPushButton[cssClass="warning"]:hover {{
                background-color: {T.WARNING_HOVER};
            }}

            QPushButton[cssClass="warning"]:pressed {{
                background-color: #92400E;
            }}

            /* ── Small Button Size Modifier ────────────── */
            QPushButton[cssSize="small"] {{
                min-height: {T.BUTTON_HEIGHT_SMALL}px;
                padding: 2px 8px;
                font-size: {T.FONT_SIZE_SMALL};
            }}

            /* ═══════════════════════════════════════════
               TEXT INPUTS
               ═══════════════════════════════════════════ */
            QLineEdit, QTextEdit, QPlainTextEdit {{
                background-color: {T.SURFACE};
                color: {T.TEXT_PRIMARY};
                border: 1px solid {T.BORDER_DEFAULT};
                padding: 5px 8px;
                border-radius: {T.BORDER_RADIUS_INPUT};
                font-size: {T.FONT_SIZE_NORMAL};
                selection-background-color: {T.ACCENT_PRIMARY_LIGHT};
            }}

            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                border: 2px solid {T.BORDER_FOCUS};
                padding: 4px 7px;
            }}

            QLineEdit:disabled, QTextEdit:disabled {{
                background-color: {T.BACKGROUND_SECONDARY};
                color: {T.TEXT_MUTED};
            }}

            QLineEdit::placeholder {{
                color: {T.TEXT_MUTED};
            }}

            /* ═══════════════════════════════════════════
               NUMERIC / DATE / TIME INPUTS
               ═══════════════════════════════════════════ */
            QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit, QDateTimeEdit {{
                background-color: {T.SURFACE};
                color: {T.TEXT_PRIMARY};
                border: 1px solid {T.BORDER_DEFAULT};
                padding: 4px 8px;
                border-radius: {T.BORDER_RADIUS_INPUT};
            }}

            QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QTimeEdit:focus {{
                border: 2px solid {T.BORDER_FOCUS};
            }}

            QSpinBox::up-button, QDoubleSpinBox::up-button,
            QDateEdit::up-button, QTimeEdit::up-button {{
                border: none;
                background-color: {T.BACKGROUND_SECONDARY};
                border-top-right-radius: {T.BORDER_RADIUS_INPUT};
            }}

            QSpinBox::down-button, QDoubleSpinBox::down-button,
            QDateEdit::down-button, QTimeEdit::down-button {{
                border: none;
                background-color: {T.BACKGROUND_SECONDARY};
                border-bottom-right-radius: {T.BORDER_RADIUS_INPUT};
            }}

            /* ═══════════════════════════════════════════
               COMBO BOX
               ═══════════════════════════════════════════ */
            QComboBox {{
                background-color: {T.SURFACE};
                color: {T.TEXT_PRIMARY};
                border: 1px solid {T.BORDER_DEFAULT};
                padding: 4px 8px;
                border-radius: {T.BORDER_RADIUS_INPUT};
                min-height: 20px;
            }}

            QComboBox:focus {{
                border: 2px solid {T.BORDER_FOCUS};
            }}

            QComboBox::drop-down {{
                border: none;
                background-color: {T.BACKGROUND_SECONDARY};
                width: 24px;
                border-top-right-radius: {T.BORDER_RADIUS_INPUT};
                border-bottom-right-radius: {T.BORDER_RADIUS_INPUT};
            }}

            QComboBox QAbstractItemView {{
                background-color: {T.SURFACE};
                border: 1px solid {T.BORDER_DEFAULT};
                selection-background-color: {T.ACCENT_PRIMARY_LIGHT};
                selection-color: {T.ACCENT_PRIMARY};
                outline: none;
            }}

            /* ═══════════════════════════════════════════
               TABLES - Card-based row design
               ═══════════════════════════════════════════ */
            QTableWidget, QTableView {{
                background-color: {T.SURFACE};
                alternate-background-color: {T.SURFACE};
                gridline-color: transparent;
                selection-background-color: {T.ACCENT_PRIMARY_LIGHT};
                selection-color: {T.ACCENT_PRIMARY};
                border: 1px solid {T.BORDER_LIGHT};
                border-radius: {T.BORDER_RADIUS_CARD};
                outline: none;
            }}

            QTableWidget::item, QTableView::item {{
                padding: 4px 8px;
                border-bottom: 1px solid {T.BORDER_LIGHT};
                color: {T.TEXT_PRIMARY};
            }}

            QTableWidget::item:hover, QTableView::item:hover {{
                background-color: {T.SURFACE_HOVER};
            }}

            QTableWidget::item:selected, QTableView::item:selected {{
                background-color: {T.ACCENT_PRIMARY_LIGHT};
                color: {T.ACCENT_PRIMARY};
            }}

            /* ── Table Headers ────────────────────────── */
            QHeaderView {{
                background-color: transparent;
            }}

            QHeaderView::section {{
                background-color: {T.BACKGROUND_SECONDARY};
                color: {T.TEXT_SECONDARY};
                padding: 6px 8px;
                border: none;
                border-bottom: 2px solid {T.ACCENT_PRIMARY};
                font-weight: 700;
                font-size: {T.FONT_SIZE_SMALL};
                text-transform: uppercase;
            }}

            QHeaderView::section:hover {{
                background-color: {T.BORDER_LIGHT};
            }}

            /* ═══════════════════════════════════════════
               TREE WIDGETS
               ═══════════════════════════════════════════ */
            QTreeWidget, QTreeView {{
                background-color: {T.SURFACE};
                alternate-background-color: {T.SURFACE};
                border: 1px solid {T.BORDER_LIGHT};
                border-radius: {T.BORDER_RADIUS_CARD};
                selection-background-color: {T.ACCENT_PRIMARY_LIGHT};
                selection-color: {T.ACCENT_PRIMARY};
                outline: none;
            }}

            QTreeWidget::item, QTreeView::item {{
                padding: 4px 6px;
                border-bottom: 1px solid {T.BORDER_LIGHT};
                min-height: 22px;
            }}

            QTreeWidget::item:hover, QTreeView::item:hover {{
                background-color: {T.SURFACE_HOVER};
            }}

            QTreeWidget::item:selected, QTreeView::item:selected {{
                background-color: {T.ACCENT_PRIMARY_LIGHT};
                color: {T.ACCENT_PRIMARY};
            }}

            /* ═══════════════════════════════════════════
               GROUP BOX
               ═══════════════════════════════════════════ */
            QGroupBox {{
                border: 1px solid {T.BORDER_DEFAULT};
                border-radius: {T.BORDER_RADIUS_CARD};
                margin-top: 10px;
                padding: 10px 8px 8px 8px;
                font-weight: 600;
                font-size: {T.FONT_SIZE_LABEL};
                color: {T.TEXT_PRIMARY};
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 6px;
                background-color: {T.BACKGROUND_PRIMARY};
                color: {T.ACCENT_PRIMARY};
                font-weight: 700;
            }}

            /* ═══════════════════════════════════════════
               MENU BAR - Dark Slate Nav
               ═══════════════════════════════════════════ */
            QMenuBar {{
                background-color: {T.NAV_BACKGROUND};
                color: {T.NAV_TEXT};
                padding: 2px 0px;
                font-weight: 600;
                font-size: {T.FONT_SIZE_LABEL};
                border: none;
            }}

            QMenuBar::item {{
                background: transparent;
                padding: 5px 12px;
                color: {T.NAV_TEXT};
                border-radius: 4px;
                margin: 2px 1px;
            }}

            QMenuBar::item:selected {{
                background-color: rgba(255, 255, 255, 0.12);
                color: {T.TEXT_INVERSE};
            }}

            QMenuBar::item:pressed {{
                background-color: rgba(255, 255, 255, 0.18);
            }}

            /* ── Dropdown Menus ───────────────────────── */
            QMenu {{
                background-color: {T.SURFACE};
                color: {T.TEXT_PRIMARY};
                border: 1px solid {T.BORDER_DEFAULT};
                border-radius: {T.BORDER_RADIUS_CARD};
                padding: 4px 0px;
            }}

            QMenu::item {{
                padding: 5px 20px 5px 10px;
                font-size: {T.FONT_SIZE_NORMAL};
            }}

            QMenu::item:selected {{
                background-color: {T.ACCENT_PRIMARY_LIGHT};
                color: {T.ACCENT_PRIMARY};
            }}

            QMenu::separator {{
                height: 1px;
                background-color: {T.BORDER_LIGHT};
                margin: 4px 8px;
            }}

            /* ═══════════════════════════════════════════
               TABS - Flat style
               ═══════════════════════════════════════════ */
            QTabWidget {{
                background-color: {T.BACKGROUND_PRIMARY};
            }}

            QTabWidget::pane {{
                border: 1px solid {T.BORDER_LIGHT};
                border-top: none;
                background-color: {T.BACKGROUND_PRIMARY};
                border-bottom-left-radius: {T.BORDER_RADIUS_CARD};
                border-bottom-right-radius: {T.BORDER_RADIUS_CARD};
            }}

            QTabBar {{
                background-color: transparent;
            }}

            QTabBar::tab {{
                background-color: transparent;
                color: {T.TEXT_SECONDARY};
                padding: 6px 16px;
                margin-right: 0px;
                border: none;
                border-bottom: 3px solid transparent;
                font-weight: 500;
                font-size: {T.FONT_SIZE_LABEL};
            }}

            QTabBar::tab:hover {{
                color: {T.TEXT_PRIMARY};
                background-color: {T.SURFACE_HOVER};
                border-bottom: 3px solid {T.BORDER_DEFAULT};
            }}

            QTabBar::tab:selected {{
                color: {T.ACCENT_PRIMARY};
                font-weight: 700;
                border-bottom: 3px solid {T.ACCENT_PRIMARY};
                background-color: transparent;
            }}

            /* ═══════════════════════════════════════════
               SCROLL BARS - Thin modern style
               ═══════════════════════════════════════════ */
            QScrollBar:vertical {{
                background-color: transparent;
                width: 8px;
                margin: 0px;
            }}

            QScrollBar::handle:vertical {{
                background-color: {T.BORDER_DEFAULT};
                border-radius: 4px;
                min-height: 30px;
            }}

            QScrollBar::handle:vertical:hover {{
                background-color: {T.TEXT_MUTED};
            }}

            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}

            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}

            QScrollBar:horizontal {{
                background-color: transparent;
                height: 8px;
                margin: 0px;
            }}

            QScrollBar::handle:horizontal {{
                background-color: {T.BORDER_DEFAULT};
                border-radius: 4px;
                min-width: 30px;
            }}

            QScrollBar::handle:horizontal:hover {{
                background-color: {T.TEXT_MUTED};
            }}

            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}

            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
                background: none;
            }}

            /* ═══════════════════════════════════════════
               FRAMES - Card & Filter Panel variants
               ═══════════════════════════════════════════ */
            QFrame {{
                background-color: transparent;
            }}

            QFrame[cssClass="card"] {{
                background-color: {T.SURFACE};
                border: 1px solid {T.BORDER_LIGHT};
                border-radius: {T.BORDER_RADIUS_CARD};
                padding: 10px;
            }}

            QFrame[cssClass="filter-panel"] {{
                background-color: {T.BACKGROUND_SECONDARY};
                border: 1px solid {T.BORDER_LIGHT};
                border-radius: {T.BORDER_RADIUS_CARD};
                padding: 8px;
            }}

            /* ═══════════════════════════════════════════
               CHECK BOX / RADIO BUTTON
               ═══════════════════════════════════════════ */
            QCheckBox {{
                color: {T.TEXT_PRIMARY};
                spacing: 6px;
                background-color: transparent;
            }}

            QCheckBox::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 2px solid {T.BORDER_DEFAULT};
                background-color: {T.SURFACE};
            }}

            QCheckBox::indicator:checked {{
                background-color: {T.ACCENT_PRIMARY};
                border-color: {T.ACCENT_PRIMARY};
            }}

            QCheckBox::indicator:hover {{
                border-color: {T.ACCENT_PRIMARY};
            }}

            QRadioButton {{
                color: {T.TEXT_PRIMARY};
                spacing: 6px;
                background-color: transparent;
            }}

            QRadioButton::indicator {{
                width: 16px;
                height: 16px;
                border-radius: 8px;
                border: 2px solid {T.BORDER_DEFAULT};
                background-color: {T.SURFACE};
            }}

            QRadioButton::indicator:checked {{
                background-color: {T.ACCENT_PRIMARY};
                border-color: {T.ACCENT_PRIMARY};
            }}

            QRadioButton::indicator:hover {{
                border-color: {T.ACCENT_PRIMARY};
            }}

            /* ═══════════════════════════════════════════
               MESSAGE BOX / DIALOG
               ═══════════════════════════════════════════ */
            QMessageBox {{
                background-color: {T.BACKGROUND_PRIMARY};
            }}

            QMessageBox QLabel {{
                color: {T.TEXT_PRIMARY};
                font-size: {T.FONT_SIZE_NORMAL};
            }}

            QMessageBox QPushButton {{
                min-width: 80px;
            }}

            /* ═══════════════════════════════════════════
               TOOL TIP
               ═══════════════════════════════════════════ */
            QToolTip {{
                background-color: {T.NAV_BACKGROUND};
                color: {T.NAV_TEXT};
                border: none;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: {T.FONT_SIZE_SMALL};
            }}

            /* ═══════════════════════════════════════════
               PROGRESS BAR
               ═══════════════════════════════════════════ */
            QProgressBar {{
                background-color: {T.BACKGROUND_SECONDARY};
                border: none;
                border-radius: 4px;
                text-align: center;
                color: {T.TEXT_PRIMARY};
                min-height: 8px;
                max-height: 8px;
            }}

            QProgressBar::chunk {{
                background-color: {T.ACCENT_PRIMARY};
                border-radius: 4px;
            }}

            /* ═══════════════════════════════════════════
               STATUS BAR
               ═══════════════════════════════════════════ */
            QStatusBar {{
                background-color: {T.BACKGROUND_SECONDARY};
                color: {T.TEXT_SECONDARY};
                border-top: 1px solid {T.BORDER_LIGHT};
                font-size: {T.FONT_SIZE_SMALL};
            }}

            /* ═══════════════════════════════════════════
               SPLITTER
               ═══════════════════════════════════════════ */
            QSplitter::handle {{
                background-color: {T.BORDER_LIGHT};
            }}

            QSplitter::handle:horizontal {{
                width: 2px;
            }}

            QSplitter::handle:vertical {{
                height: 2px;
            }}
        """
