"""Pharmacogenomic Dashboard - Overview of drug-gene conflicts, variants, and queue status"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from config import Theme


class PgxDashboardView(QWidget):
    """Dashboard showing pharmacogenomic stats and queue health"""

    def __init__(self, db_connection, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.setWindowTitle("Pharmacogenomic Dashboard")
        self.setMinimumSize(1000, 700)
        self.init_ui()
        self.load_data()

    def init_ui(self):
        """Initialize the dashboard UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            Theme.MARGIN_NORMAL, Theme.MARGIN_NORMAL,
            Theme.MARGIN_NORMAL, Theme.MARGIN_NORMAL
        )
        layout.setSpacing(Theme.SPACING_NORMAL)

        # Title
        title = QLabel("Pharmacogenomic Dashboard")
        title.setProperty("cssClass", "page-title")
        layout.addWidget(title)

        # Top row: summary cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(Theme.SPACING_NORMAL)

        self.conflict_count_label = QLabel("0")
        cards_layout.addWidget(self._create_stat_card(
            "Active Drug-Gene Conflicts", self.conflict_count_label
        ))

        self.high_risk_count_label = QLabel("0")
        cards_layout.addWidget(self._create_stat_card(
            "High-Risk Patients", self.high_risk_count_label
        ))

        self.pending_review_label = QLabel("0")
        cards_layout.addWidget(self._create_stat_card(
            "Pending Drug Reviews", self.pending_review_label
        ))

        self.verification_pending_label = QLabel("0")
        cards_layout.addWidget(self._create_stat_card(
            "Awaiting Verification", self.verification_pending_label
        ))

        layout.addLayout(cards_layout)

        # Middle row: top-10 tables
        tables_layout = QHBoxLayout()
        tables_layout.setSpacing(Theme.SPACING_NORMAL)

        # Top flagged medications
        med_group = QGroupBox("Top 10 Flagged Medications")
        med_layout = QVBoxLayout()
        self.flagged_meds_table = QTableWidget()
        self.flagged_meds_table.setColumnCount(2)
        self.flagged_meds_table.setHorizontalHeaderLabels(["Medication", "Flag Count"])
        self.flagged_meds_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.flagged_meds_table.setShowGrid(False)
        self.flagged_meds_table.verticalHeader().setVisible(False)
        self.flagged_meds_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        med_layout.addWidget(self.flagged_meds_table)
        med_group.setLayout(med_layout)
        tables_layout.addWidget(med_group)

        # Top genetic variants
        var_group = QGroupBox("Top 10 Genetic Variants")
        var_layout = QVBoxLayout()
        self.variants_table = QTableWidget()
        self.variants_table.setColumnCount(3)
        self.variants_table.setHorizontalHeaderLabels(["Gene", "Variant", "Count"])
        self.variants_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.variants_table.setShowGrid(False)
        self.variants_table.verticalHeader().setVisible(False)
        self.variants_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        var_layout.addWidget(self.variants_table)
        var_group.setLayout(var_layout)
        tables_layout.addWidget(var_group)

        layout.addLayout(tables_layout)

        # Bottom row: queue status summary
        queue_group = QGroupBox("Queue Status Summary")
        queue_layout = QVBoxLayout()
        self.queue_table = QTableWidget()
        self.queue_table.setColumnCount(2)
        self.queue_table.setHorizontalHeaderLabels(["Workflow Stage", "Count"])
        self.queue_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.queue_table.setShowGrid(False)
        self.queue_table.verticalHeader().setVisible(False)
        self.queue_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        queue_layout.addWidget(self.queue_table)
        queue_group.setLayout(queue_layout)
        layout.addWidget(queue_group)

        # Refresh button
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        refresh_btn = QPushButton("Refresh")
        refresh_btn.setProperty("cssClass", "secondary")
        refresh_btn.clicked.connect(self.load_data)
        btn_layout.addWidget(refresh_btn)
        layout.addLayout(btn_layout)

    def _create_stat_card(self, title, value_label):
        """Create a stat card with title and value"""
        group = QGroupBox(title)
        group_layout = QVBoxLayout()
        value_label.setProperty("cssClass", "page-title")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        group_layout.addWidget(value_label)
        group.setLayout(group_layout)
        return group

    def load_data(self):
        """Load all dashboard data"""
        if not self.db_connection:
            return

        try:
            cursor = self.db_connection.cursor

            # Active drug-gene conflicts count
            cursor.execute("SELECT COUNT(*) as count FROM drugreviewqueue WHERE status = 'pending'")
            self.pending_review_label.setText(str(cursor.fetchone().get('count', 0)))

            # Active conflicts in drug_review
            cursor.execute("SELECT COUNT(*) as count FROM drug_review WHERE status = 'active'")
            self.conflict_count_label.setText(str(cursor.fetchone().get('count', 0)))

            # High-risk patients (patients with any high-risk variant)
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) as count FROM drug_review
                WHERE risk_level = 'High' AND status = 'active'
            """)
            self.high_risk_count_label.setText(str(cursor.fetchone().get('count', 0)))

            # Verification pending count
            cursor.execute(
                "SELECT COUNT(*) as count FROM ActivatedPrescriptions WHERE status = 'verification_pending'"
            )
            self.verification_pending_label.setText(str(cursor.fetchone().get('count', 0)))

            # Top 10 flagged medications
            cursor.execute("""
                SELECT m.medication_name, COUNT(*) as flag_count
                FROM drug_review dr
                JOIN medications m ON dr.medication_id = m.medication_id
                WHERE dr.status = 'active'
                GROUP BY m.medication_name
                ORDER BY flag_count DESC
                LIMIT 10
            """)
            flagged_meds = cursor.fetchall()
            self.flagged_meds_table.setRowCount(len(flagged_meds))
            for i, row in enumerate(flagged_meds):
                self.flagged_meds_table.setItem(i, 0, QTableWidgetItem(row.get('medication_name', '')))
                self.flagged_meds_table.setItem(i, 1, QTableWidgetItem(str(row.get('flag_count', 0))))

            # Top 10 genetic variants
            cursor.execute("""
                SELECT gene, variant, COUNT(*) as variant_count
                FROM final_genetic_info
                GROUP BY gene, variant
                ORDER BY variant_count DESC
                LIMIT 10
            """)
            variants = cursor.fetchall()
            self.variants_table.setRowCount(len(variants))
            for i, row in enumerate(variants):
                self.variants_table.setItem(i, 0, QTableWidgetItem(row.get('gene', '')))
                self.variants_table.setItem(i, 1, QTableWidgetItem(row.get('variant', '')))
                self.variants_table.setItem(i, 2, QTableWidgetItem(str(row.get('variant_count', 0))))

            # Queue status summary
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM ActivatedPrescriptions
                GROUP BY status
                ORDER BY count DESC
            """)
            queue_stats = cursor.fetchall()
            self.queue_table.setRowCount(len(queue_stats))
            for i, row in enumerate(queue_stats):
                status = row.get('status', '').replace('_', ' ').title()
                self.queue_table.setItem(i, 0, QTableWidgetItem(status))
                self.queue_table.setItem(i, 1, QTableWidgetItem(str(row.get('count', 0))))

        except Exception as e:
            QMessageBox.critical(self, "Dashboard Error", str(e))
            print(f"Error loading dashboard: {e}")

    def refresh(self):
        """Refresh dashboard data"""
        self.load_data()
