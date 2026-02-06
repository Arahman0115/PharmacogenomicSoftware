from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QTableWidget, QTableWidgetItem, QHeaderView


class DrugReviewTab(QWidget):
    """Drug Review / Drug-Gene Interactions tab"""

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

        group = QGroupBox("Drug-Gene Interactions & Warnings")
        group_layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Medication", "Gene", "Variant", "Risk Level", "Notes"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        group_layout.addWidget(self.table)
        group.setLayout(group_layout)
        layout.addWidget(group)

    def load_drug_interactions(self):
        """Load drug-gene interactions from database"""
        if not self.db_connection or not self.user_id:
            return

        try:
            query = """
                SELECT dr.*, m.medication_name, fg.gene, fg.variant
                FROM drug_review dr
                JOIN medications m ON dr.medication_id = m.medication_id
                LEFT JOIN final_genetic_info fg ON dr.user_id = fg.user_id
                WHERE dr.user_id = %s
                ORDER BY dr.risk_level DESC
            """
            self.db_connection.cursor.execute(query, (self.user_id,))
            interactions = self.db_connection.cursor.fetchall()

            self.table.setRowCount(len(interactions))
            for row, interaction in enumerate(interactions):
                self.table.setItem(row, 0, QTableWidgetItem(interaction.get('medication_name', '')))
                self.table.setItem(row, 1, QTableWidgetItem(interaction.get('gene', '')))
                self.table.setItem(row, 2, QTableWidgetItem(interaction.get('variant', '')))
                self.table.setItem(row, 3, QTableWidgetItem(interaction.get('risk_level', '')))
                self.table.setItem(row, 4, QTableWidgetItem(interaction.get('notes', '')))

        except Exception as e:
            print(f"Error loading drug interactions: {e}")
