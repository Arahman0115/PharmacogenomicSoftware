from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QPushButton, QLabel, QScrollArea
)
from PyQt6.QtCore import Qt
from config.theme import Theme


class DrugReviewTab(QWidget):
    """Drug Review / Drug-Gene Interactions tab with collapsible risk level sections"""

    def __init__(self, db_connection=None, user_id=None):
        super().__init__()
        self.db_connection = db_connection
        self.user_id = user_id
        self.init_ui()
        if db_connection and user_id:
            self.load_drug_interactions()

    def init_ui(self):
        """Initialize the tab UI"""
        layout = QVBoxLayout(self)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setProperty("cssClass", "secondary")
        refresh_btn.clicked.connect(self.load_drug_interactions)
        button_layout.addWidget(refresh_btn)

        layout.addLayout(button_layout)

        # Scrollable area for risk level sections
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_widget)
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

    def load_drug_interactions(self):
        """Load drug-gene interactions organized by risk level"""
        if not self.db_connection or not self.user_id:
            return

        try:
            # Clear existing risk level groups
            while self.scroll_layout.count():
                item = self.scroll_layout.takeAt(0)
                if item.widget():
                    item.widget().deleteLater()

            query = """
                SELECT dr.medication_id, m.medication_name, dr.gene, dr.variant,
                       dr.risk_level, dr.notes
                FROM drug_review dr
                JOIN medications m ON dr.medication_id = m.medication_id
                WHERE dr.user_id = %s AND dr.status = 'active'
                ORDER BY FIELD(dr.risk_level, 'High', 'Moderate', 'Low'), m.medication_name
            """
            self.db_connection.cursor.execute(query, (self.user_id,))
            interactions = self.db_connection.cursor.fetchall()

            if not interactions:
                no_data_label = QLabel("No drug-gene interactions found")
                no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.scroll_layout.addWidget(no_data_label)
                return

            # Group by risk level and medication
            grouped = self._group_interactions(interactions)

            # Create collapsible sections for each risk level
            risk_level_order = ['High', 'Moderate', 'Low']
            for risk_level in risk_level_order:
                if risk_level not in grouped or not grouped[risk_level]:
                    continue

                group = self._create_risk_level_group(risk_level, grouped[risk_level])
                self.scroll_layout.addWidget(group)

            self.scroll_layout.addStretch()

        except Exception as e:
            print(f"Error loading drug interactions: {e}")

    def _group_interactions(self, interactions):
        """Group interactions by risk level and medication"""
        grouped = {'High': {}, 'Moderate': {}, 'Low': {}}

        for interaction in interactions:
            risk = interaction.get('risk_level', 'Low')
            med_name = interaction.get('medication_name', 'Unknown')

            if risk not in grouped:
                grouped[risk] = {}

            if med_name not in grouped[risk]:
                grouped[risk][med_name] = []

            grouped[risk][med_name].append(interaction)

        return grouped

    def _create_risk_level_group(self, risk_level, medications):
        """Create a collapsible group for a risk level"""
        # Determine color based on risk level
        if risk_level == 'High':
            bg_color = Theme.ERROR_LIGHT
            border_color = Theme.ERROR
            text_color = "#FF6B6B"
        elif risk_level == 'Moderate':
            bg_color = Theme.WARNING_LIGHT
            border_color = Theme.WARNING
            text_color = "#FFB84D"
        else:  # Low
            bg_color = Theme.SUCCESS_LIGHT
            border_color = Theme.SUCCESS
            text_color = "#51CF66"

        med_count = sum(len(vars) for vars in medications.values())
        group = QGroupBox(f"{risk_level} Risk ({med_count} medication{'s' if med_count != 1 else ''})")
        group.setCheckable(True)
        group.setChecked(risk_level == 'High')  # Expand High Risk by default
        group.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid {border_color};
                border-radius: 4px;
                margin-top: 8px;
                padding-top: 12px;
                background-color: {bg_color};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 4px;
                color: {text_color};
                font-weight: bold;
            }}
        """)

        layout = QVBoxLayout(group)

        # Add table for this risk level
        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Medication", "Gene", "Variant", "Notes"])
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        table.setShowGrid(False)

        row = 0
        for med_name, interactions in sorted(medications.items()):
            for interaction in interactions:
                table.insertRow(row)
                table.setItem(row, 0, QTableWidgetItem(med_name))
                table.setItem(row, 1, QTableWidgetItem(interaction.get('gene', '')))
                table.setItem(row, 2, QTableWidgetItem(interaction.get('variant', '')))
                table.setItem(row, 3, QTableWidgetItem(interaction.get('notes', '')))
                row += 1

        table.setMaximumHeight(row * 36)
        layout.addWidget(table)
        return group
