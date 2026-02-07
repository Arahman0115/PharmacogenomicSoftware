"""Business logic for prescription processing

Extracted from EditPrescriptionsView.py and other queue views
Centralizes all prescription-related operations
"""


class PrescriptionService:
    """Service layer for prescription operations"""

    def __init__(self, db_connection):
        self.db_connection = db_connection

    def load_prescription_data(self, prescription_id):
        """Load prescription with patient and prescriber info"""
        try:
            query = """
                SELECT p.*, m.medication_name, CONCAT(pr.last_name, ', ', pr.first_name) as prescriber_name
                FROM Prescriptions p
                LEFT JOIN medications m ON p.medication_id = m.medication_id
                LEFT JOIN Prescribers pr ON p.prescriber_id = pr.prescriber_id
                WHERE p.prescription_id = %s
            """
            self.db_connection.cursor.execute(query, (prescription_id,))
            return self.db_connection.cursor.fetchone()
        except Exception as e:
            print(f"Error loading prescription: {e}")
            return None

    def select_bottle(self, prescription_id, bottle_id):
        """Assign bottle to prescription"""
        try:
            query = """
                UPDATE Prescriptions
                SET bottle_id = %s, status = 'bottle_selected'
                WHERE prescription_id = %s
            """
            self.db_connection.cursor.execute(query, (bottle_id, prescription_id))
            self.db_connection.connection.commit()
            return True
        except Exception as e:
            print(f"Error selecting bottle: {e}")
            self.db_connection.connection.rollback()
            return False

    def process_to_drug_review(self, prescription_id):
        """Move prescription to drug review queue"""
        try:
            query = """
                UPDATE Prescriptions
                SET status = 'drug_review_pending'
                WHERE prescription_id = %s
            """
            self.db_connection.cursor.execute(query, (prescription_id,))
            self.db_connection.connection.commit()
            return True
        except Exception as e:
            print(f"Error processing to drug review: {e}")
            self.db_connection.connection.rollback()
            return False

    def check_inventory(self, medication_id):
        """Check available bottles for medication"""
        try:
            query = """
                SELECT b.bottle_id, b.quantity, b.expiration_date, b.ndc
                FROM bottles b
                WHERE b.medication_id = %s
                AND b.quantity > 0
                AND b.expiration_date > CURDATE()
                AND b.status = 'in_stock'
                ORDER BY b.expiration_date ASC
            """
            self.db_connection.cursor.execute(query, (medication_id,))
            return self.db_connection.cursor.fetchall()
        except Exception as e:
            print(f"Error checking inventory: {e}")
            return []

    def get_drug_gene_interactions(self, prescription_id):
        """Get drug-gene interaction warnings for prescription"""
        try:
            query = """
                SELECT dr.*, p.medication_id, fg.gene, fg.variant
                FROM Prescriptions p
                LEFT JOIN drug_review dr ON p.medication_id = dr.medication_id
                LEFT JOIN final_genetic_info fg ON p.user_id = fg.user_id
                WHERE p.prescription_id = %s
            """
            self.db_connection.cursor.execute(query, (prescription_id,))
            return self.db_connection.cursor.fetchall()
        except Exception as e:
            print(f"Error getting drug-gene interactions: {e}")
            return []

    def get_patient_genomic_data(self, user_id):
        """Get patient's genetic test results"""
        try:
            query = """
                SELECT *
                FROM final_genetic_info
                WHERE user_id = %s
                ORDER BY date_tested DESC
            """
            self.db_connection.cursor.execute(query, (user_id,))
            return self.db_connection.cursor.fetchall()
        except Exception as e:
            print(f"Error getting genomic data: {e}")
            return []

    def complete_prescription(self, prescription_id, payment_method=None):
        """Mark prescription as completed and dispensed"""
        try:
            query = """
                UPDATE Prescriptions
                SET status = 'completed', dispensed_date = NOW()
                WHERE prescription_id = %s
            """
            self.db_connection.cursor.execute(query, (prescription_id,))
            self.db_connection.connection.commit()
            return True
        except Exception as e:
            print(f"Error completing prescription: {e}")
            self.db_connection.connection.rollback()
            return False

    def get_prescription_queue(self, queue_type, user_id=None, limit=50, offset=0):
        """Get prescriptions for a specific queue"""
        try:
            query_map = {
                'reception': "SELECT * FROM ProductSelectionQueue WHERE status = 'pending'",
                'data_entry': "SELECT * FROM ProductSelectionQueue WHERE status IN ('pending', 'in_progress')",
                'drug_review': "SELECT * FROM drugreviewqueue WHERE status = 'pending'",
                'release': "SELECT * FROM ReadyForPickUp WHERE status = 'pending'",
            }

            query = query_map.get(queue_type)
            if not query:
                raise ValueError(f"Unknown queue type: {queue_type}")

            query += f" ORDER BY created_date ASC LIMIT {limit} OFFSET {offset}"
            self.db_connection.cursor.execute(query)
            return self.db_connection.cursor.fetchall()
        except Exception as e:
            print(f"Error getting prescription queue: {e}")
            return []

    def refill_prescription(self, prescription_id, new_quantity=None):
        """Process prescription refill"""
        try:
            # Get original prescription details
            original = self.load_prescription_data(prescription_id)
            if not original:
                return False

            # Create new prescription with refill
            insert_query = """
                INSERT INTO Prescriptions
                (user_id, medication_id, quantity, refills_remaining, prescriber_id, status)
                VALUES (%s, %s, %s, %s, %s, 'pending')
            """
            quantity = new_quantity or original.get('quantity', 0)
            refills = max(0, original.get('refills_remaining', 0) - 1)

            self.db_connection.cursor.execute(
                insert_query,
                (
                    original.get('user_id'),
                    original.get('medication_id'),
                    quantity,
                    refills,
                    original.get('prescriber_id')
                )
            )
            self.db_connection.connection.commit()
            return True
        except Exception as e:
            print(f"Error refilling prescription: {e}")
            self.db_connection.connection.rollback()
            return False
