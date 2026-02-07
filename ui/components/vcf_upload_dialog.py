"""VCF Upload Dialog - Upload and process VCF files for genetic variants"""
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox,
    QFileDialog, QProgressDialog, QTextEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from ui.utils.vcf_parser import VCFParser
from services.pharmgkb_service import PharmGKBService
from datetime import datetime


class VCFProcessWorker(QThread):
    """Background worker to process VCF file"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)  # Emits dict with 'variants' and 'interactions'
    error = pyqtSignal(str)

    def __init__(self, vcf_file_path: str):
        super().__init__()
        self.vcf_file_path = vcf_file_path

    def run(self):
        """Parse VCF and query PharmGKB"""
        try:
            # Step 1: Parse VCF
            self.progress.emit("Parsing VCF file...")
            parser = VCFParser(self.vcf_file_path)
            variants = parser.parse()

            if not variants:
                self.error.emit("No variants found in VCF file")
                return

            self.progress.emit(f"Found {len(variants)} variants. Querying PharmGKB...")

            # Step 2: Query PharmGKB for each variant
            service = PharmGKBService()
            all_interactions = []

            for variant in variants:
                variant_id = variant.get('rsid', '')
                if not variant_id:
                    continue

                self.progress.emit(f"Querying PharmGKB for {variant_id}...")
                conflicts, success = service.get_variant_annotations(variant_id)

                if success and conflicts:
                    for conflict in conflicts:
                        interaction = {
                            'drug_name': conflict['medication_name'],
                            'gene': variant.get('gene', 'Unknown'),
                            'variant': variant_id,
                            'risk_level': conflict['risk_level'],
                            'clinical_annotation': conflict['sentence'],
                            'dosing_guideline': conflict.get('pgkb_url', '')
                        }
                        all_interactions.append(interaction)

            # Step 3: Prepare drug_review entries AND variant entries
            self.progress.emit(f"Processing {len(variants)} variants...")

            drug_review_entries = []
            variant_entries = []

            # Add all variants to genomics tab (regardless of interactions)
            for variant in variants:
                variant_entry = {
                    'gene': variant.get('gene', 'Unknown'),
                    'variant': variant.get('rsid', ''),
                    'genotype': variant.get('genotype', 'Unknown'),
                    'source': 'vcf_upload'
                }
                variant_entries.append(variant_entry)

            # Add any interactions found to drug review
            if all_interactions:
                for interaction in all_interactions:
                    entry = {
                        'medication_name': interaction['drug_name'],
                        'gene': interaction['gene'],
                        'variant': interaction['variant'],
                        'risk_level': interaction['risk_level'],
                        'description': interaction['clinical_annotation'],
                        'notes': interaction['dosing_guideline']
                    }
                    drug_review_entries.append(entry)

            # Combine results: variants + interactions
            result = {
                'variants': variant_entries,
                'interactions': drug_review_entries
            }

            summary = f"Found {len(variant_entries)} variants. "
            if drug_review_entries:
                summary += f"{len(drug_review_entries)} drug interactions detected."
            else:
                summary += "No drug interactions found in PharmGKB."

            self.progress.emit(f"Processing complete! {summary}")
            self.finished.emit(result)

        except Exception as e:
            self.error.emit(str(e))


class VCFUploadDialog(QDialog):
    """Dialog for uploading and processing VCF files"""

    def __init__(self, db_connection, user_id: int, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.user_id = user_id
        self.vcf_file_path = None
        self.variants = []
        self.drug_interactions = []
        self.worker = None

        self.setWindowTitle(f"Upload VCF File - Patient {user_id}")
        self.setGeometry(100, 100, 700, 500)
        self.init_ui()

    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout(self)

        # File selection
        file_layout = QHBoxLayout()
        self.file_label = QLabel("No file selected")
        file_layout.addWidget(self.file_label)

        browse_btn = QPushButton("Browse...")
        browse_btn.setProperty("cssClass", "secondary")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)

        layout.addLayout(file_layout)

        # Progress/Output
        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        self.output_text.setMaximumHeight(200)
        layout.addWidget(QLabel("Processing Log:"))
        layout.addWidget(self.output_text)

        # Summary
        self.summary_label = QLabel("")
        layout.addWidget(self.summary_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.import_btn = QPushButton("Import to Patient Profile")
        self.import_btn.setProperty("cssClass", "success")
        self.import_btn.clicked.connect(self.import_to_patient)
        self.import_btn.setEnabled(False)
        button_layout.addWidget(self.import_btn)

        upload_btn = QPushButton("Upload & Process VCF")
        upload_btn.setProperty("cssClass", "primary")
        upload_btn.clicked.connect(self.process_vcf)
        button_layout.addWidget(upload_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setProperty("cssClass", "ghost")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

    def browse_file(self):
        """Browse for VCF file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select VCF File",
            "",
            "VCF Files (*.vcf *.vcf.gz);;All Files (*)"
        )

        if file_path:
            self.vcf_file_path = file_path
            self.file_label.setText(file_path.split('/')[-1])
            self.output_text.append(f"Selected: {file_path}")

    def process_vcf(self):
        """Process VCF file in background"""
        if not self.vcf_file_path:
            QMessageBox.warning(self, "Error", "Please select a VCF file first")
            return

        # Start background worker
        self.worker = VCFProcessWorker(self.vcf_file_path)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.error.connect(self.on_error)
        self.worker.start()

    def on_progress(self, message: str):
        """Update progress"""
        self.output_text.append(message)

    def on_finished(self, result: dict):
        """VCF processing finished"""
        self.variants = result.get('variants', [])
        self.drug_interactions = result.get('interactions', [])

        summary = f"✓ Ready to import: {len(self.variants)} variants"
        if self.drug_interactions:
            summary += f", {len(self.drug_interactions)} drug interactions"

        self.summary_label.setText(summary)

        # Enable import button if variants were found
        if self.variants:
            self.import_btn.setEnabled(True)

    def on_error(self, error_message: str):
        """Handle error"""
        QMessageBox.critical(self, "Error Processing VCF", error_message)
        self.summary_label.setText(f"✗ Error: {error_message}")

    def import_to_patient(self):
        """Import variants and drug interactions to patient profile"""
        try:
            cursor = self.db_connection.cursor
            imported_variants = 0
            imported_interactions = 0

            # Step 1: Import ALL variants to genomics tab
            self.output_text.append(f"Importing {len(self.variants)} variants...")
            from datetime import datetime
            today = datetime.now().strftime('%Y-%m-%d')

            for variant in self.variants:
                cursor.execute("""
                    INSERT INTO final_genetic_info
                    (user_id, gene, variant, genotype, date_tested)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE genotype = VALUES(genotype), date_tested = VALUES(date_tested)
                """, (
                    self.user_id,
                    variant['gene'],
                    variant['variant'],
                    variant['genotype'],
                    today
                ))
                imported_variants += 1

            self.output_text.append(f"✓ Imported {imported_variants} variants to Genomics tab")

            # Step 2: Import drug interactions to drug_review
            if self.drug_interactions:
                self.output_text.append(f"Importing {len(self.drug_interactions)} drug interactions...")
                for interaction in self.drug_interactions:
                    # Use SubQuery to get medication_id - matches PharmGKBService approach
                    cursor.execute("""
                        INSERT INTO drug_review
                        (user_id, medication_id, gene, variant, risk_level, notes, status)
                        SELECT %s, m.medication_id, %s, %s, %s, %s, 'active'
                        FROM medications m
                        WHERE m.medication_name = %s
                        ON DUPLICATE KEY UPDATE
                            risk_level = VALUES(risk_level),
                            notes = VALUES(notes),
                            status = 'active'
                    """, (
                        self.user_id,
                        interaction['gene'],
                        interaction['variant'],
                        interaction['risk_level'],
                        interaction['description'] + " | " + interaction['notes'],
                        interaction['medication_name']
                    ))
                    imported_interactions += 1

                self.output_text.append(f"✓ Imported {imported_interactions} drug interactions to Drug Review tab")
            else:
                self.output_text.append("ℹ No drug interactions found - variants stored for future reference")

            self.db_connection.connection.commit()

            QMessageBox.information(
                self, "Success",
                f"Import complete!\n"
                f"✓ {imported_variants} variants added to Genomics tab\n"
                f"✓ {imported_interactions} drug interactions added to Drug Review tab"
            )

            self.accept()

        except Exception as e:
            self.db_connection.connection.rollback()
            QMessageBox.critical(self, "Import Error", f"Failed to import: {e}")
