from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QTreeWidget, QTreeWidgetItem,
    QFormLayout, QLineEdit, QPushButton, QMessageBox, QHBoxLayout, QLabel
)
from PyQt6.QtCore import Qt
from services.pharmgkb_service import PharmGKBService


class GenomicsTab(QWidget):
    """Genomic Information tab with PharmGKB integration"""

    def __init__(self, db_connection=None, user_id=None):
        super().__init__()
        self.db_connection = db_connection
        self.user_id = user_id
        self.pharmgkb_service = PharmGKBService()
        self.init_ui()
        if db_connection and user_id:
            self.load_genomic_data()

    def init_ui(self):
        """Initialize the tab UI"""
        layout = QVBoxLayout(self)

        # Upper section: Add new variant form
        add_variant_group = QGroupBox("Add Genetic Variant")
        form_layout = QFormLayout()

        self.gene_edit = QLineEdit()
        self.gene_edit.setPlaceholderText("e.g., SLCO1B1, CYP2C9")
        form_layout.addRow("Gene:", self.gene_edit)

        self.variant_edit = QLineEdit()
        self.variant_edit.setPlaceholderText("e.g., rs4149056")
        form_layout.addRow("Variant (rs number):", self.variant_edit)

        self.genotype_edit = QLineEdit()
        self.genotype_edit.setPlaceholderText("e.g., A/A, G/A")
        form_layout.addRow("Genotype:", self.genotype_edit)

        # Buttons layout
        button_layout = QHBoxLayout()

        test_btn = QPushButton("Test & Analyze")
        test_btn.setProperty("cssClass", "primary")
        test_btn.clicked.connect(self.test_variant)
        button_layout.addWidget(test_btn)

        add_btn = QPushButton("Add Variant")
        add_btn.setProperty("cssClass", "success")
        add_btn.clicked.connect(self.add_variant)
        button_layout.addWidget(add_btn)

        form_layout.addRow("", button_layout)
        add_variant_group.setLayout(form_layout)
        layout.addWidget(add_variant_group)

        # Lower section: Display existing variants and conflicts
        genomics_group = QGroupBox("Genetic Information")
        gen_layout = QVBoxLayout()

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Gene", "Genetic Variant", "Genotype", "Date Tested", "At-Risk Medications"])
        self.tree.setColumnCount(5)
        self.tree.setColumnWidth(0, 100)
        self.tree.setColumnWidth(1, 150)
        self.tree.setColumnWidth(2, 100)
        self.tree.setColumnWidth(3, 120)
        self.tree.setColumnWidth(4, 300)

        gen_layout.addWidget(self.tree)
        genomics_group.setLayout(gen_layout)
        layout.addWidget(genomics_group)

        # Info label
        info_label = QLabel(
            "Testing a variant will query PharmGKB for drug interactions. "
            "At-risk medications will be flagged in the Drug Review queue."
        )
        info_label.setProperty("cssClass", "info-label")
        layout.addWidget(info_label)

    def test_variant(self):
        """Test variant against PharmGKB without saving"""
        variant = self.variant_edit.text().strip()
        gene = self.gene_edit.text().strip()

        if not variant:
            QMessageBox.warning(self, "Input Error", "Please enter a variant (rs number)")
            return

        # Show progress
        QMessageBox.information(self, "Testing", f"Querying PharmGKB for {variant}...\nThis may take a moment.")

        # Query PharmGKB
        conflicts, success = self.pharmgkb_service.get_variant_annotations(variant)

        if not success:
            QMessageBox.critical(self, "API Error", "Failed to connect to PharmGKB API")
            return

        if not conflicts:
            QMessageBox.information(self, "Results", f"No drug interactions found for {variant}")
            return

        # Display results
        result_text = f"Found {len(conflicts)} potential medication conflicts:\n\n"
        for conflict in conflicts:
            result_text += f"• {conflict['medication_name']} (Risk: {conflict['risk_level']}, Score: {conflict['score']})\n"

        QMessageBox.information(self, "PharmGKB Results", result_text)

    def add_variant(self):
        """Add variant to patient record and create drug review entries"""
        gene = self.gene_edit.text().strip()
        variant = self.variant_edit.text().strip()
        genotype = self.genotype_edit.text().strip()

        if not gene or not variant or not genotype:
            QMessageBox.warning(self, "Input Error", "Please fill in all fields")
            return

        if not self.db_connection or not self.user_id:
            QMessageBox.critical(self, "Error", "No database connection")
            return

        # Query PharmGKB
        QMessageBox.information(self, "Processing", "Querying PharmGKB for drug interactions...")
        conflicts, success = self.pharmgkb_service.get_variant_annotations(variant)

        if not success:
            QMessageBox.critical(self, "API Error", "Failed to connect to PharmGKB API")
            return

        # Save to database
        if not conflicts:
            # Still save the variant even if no conflicts found
            try:
                cursor = self.db_connection.cursor
                cursor.execute("""
                    INSERT INTO final_genetic_info
                    (user_id, gene, variant, genotype, date_tested, test_result)
                    VALUES (%s, %s, %s, %s, CURDATE(), %s)
                """, (self.user_id, gene, variant, genotype, "No conflicts found"))
                self.db_connection.connection.commit()
                QMessageBox.information(self, "Success", f"Variant {variant} added (no drug conflicts found)")
            except Exception as e:
                QMessageBox.critical(self, "Database Error", str(e))
                return
        else:
            # Save variant and conflicts
            success = self.pharmgkb_service.save_variant_conflicts_to_db(
                self.db_connection,
                self.user_id,
                gene,
                variant,
                genotype,
                conflicts
            )

            if success:
                conflict_count = len(conflicts)
                QMessageBox.information(
                    self, "Success",
                    f"Variant {variant} added with {conflict_count} medication conflicts.\n"
                    f"These will appear as at-risk in the Drug Review queue."
                )
            else:
                QMessageBox.critical(self, "Database Error", "Failed to save variant to database")
                return

        # Clear form
        self.gene_edit.clear()
        self.variant_edit.clear()
        self.genotype_edit.clear()

        # Reload data
        self.load_genomic_data()

    def load_genomic_data(self):
        """Load genetic test results from database with drug conflicts"""
        if not self.db_connection or not self.user_id:
            return

        try:
            # Get genetic information
            query = """
                SELECT id, gene, variant, genotype, date_tested
                FROM final_genetic_info
                WHERE user_id = %s
                ORDER BY date_tested DESC
            """
            self.db_connection.cursor.execute(query, (self.user_id,))
            results = self.db_connection.cursor.fetchall()

            self.tree.clear()

            for result in results:
                genetic_id = result.get('id')
                gene = result.get('gene', '')
                variant = result.get('variant', '')
                genotype = result.get('genotype', '')
                date_tested = str(result.get('date_tested', ''))

                # Get at-risk medications for this variant
                risk_query = """
                    SELECT DISTINCT dr.medication_id, m.medication_name, dr.risk_level
                    FROM drug_review dr
                    JOIN medications m ON dr.medication_id = m.medication_id
                    WHERE dr.user_id = %s AND dr.variant = %s AND dr.status = 'active'
                """
                self.db_connection.cursor.execute(risk_query, (self.user_id, variant))
                risks = self.db_connection.cursor.fetchall()

                # Format at-risk medications
                at_risk_meds = []
                for risk in risks:
                    med_name = risk.get('medication_name', 'Unknown')
                    risk_level = risk.get('risk_level', 'Low')
                    at_risk_meds.append(f"{med_name} ({risk_level})")

                at_risk_text = "; ".join(at_risk_meds) if at_risk_meds else "None"

                # Add to tree
                item = QTreeWidgetItem([gene, variant, genotype, date_tested, at_risk_text])
                item.setData(0, Qt.ItemDataRole.UserRole, genetic_id)
                self.tree.addTopLevelItem(item)

        except Exception as e:
            print(f"Error loading genomic data: {e}")
            QMessageBox.critical(self, "Database Error", f"Failed to load genomic data: {e}")
