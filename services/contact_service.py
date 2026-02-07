"""Service for creating and managing contact requests"""


class ContactService:
    """Service for contact request operations"""

    def __init__(self, db_connection):
        self.db_connection = db_connection

    def create_refill_request(self, user_id, prescriber_id, medication_id, prescription_id, reason="Refill requested"):
        """Create a refill contact request"""
        try:
            cursor = self.db_connection.cursor

            insert_query = """
                INSERT INTO contact_requests
                (user_id, prescriber_id, prescription_id, medication_id, request_type, reason,
                 status, delivery_method, created_at)
                VALUES (%s, %s, %s, %s, 'refill', %s, 'pending', 'fax', NOW())
            """

            cursor.execute(insert_query, (
                user_id,
                prescriber_id,
                prescription_id,
                medication_id,
                reason
            ))

            self.db_connection.connection.commit()
            return True

        except Exception as e:
            self.db_connection.connection.rollback()
            print(f"Error creating refill request: {e}")
            return False

    def create_clarification_request(self, user_id, prescriber_id, prescription_id, medication_id, reason):
        """Create an Rx clarification contact request"""
        try:
            cursor = self.db_connection.cursor

            insert_query = """
                INSERT INTO contact_requests
                (user_id, prescriber_id, prescription_id, medication_id, request_type, reason,
                 status, delivery_method, created_at)
                VALUES (%s, %s, %s, %s, 'rx_clarification', %s, 'pending', 'fax', NOW())
            """

            cursor.execute(insert_query, (
                user_id,
                prescriber_id,
                prescription_id,
                medication_id,
                reason
            ))

            self.db_connection.connection.commit()
            return True

        except Exception as e:
            self.db_connection.connection.rollback()
            print(f"Error creating clarification request: {e}")
            return False

    def create_genetic_info_request(self, user_id, reason="Genetic information needed for pharmacogenomics analysis"):
        """Create a genetic information contact request"""
        try:
            cursor = self.db_connection.cursor

            insert_query = """
                INSERT INTO contact_requests
                (user_id, request_type, reason, status, delivery_method, created_at)
                VALUES (%s, 'genetic_info', %s, 'pending', 'fax', NOW())
            """

            cursor.execute(insert_query, (user_id, reason))

            self.db_connection.connection.commit()
            return True

        except Exception as e:
            self.db_connection.connection.rollback()
            print(f"Error creating genetic info request: {e}")
            return False

    def check_existing_request(self, user_id, request_type, prescription_id=None):
        """Check if a similar request already exists and is pending"""
        try:
            cursor = self.db_connection.cursor

            if prescription_id:
                query = """
                    SELECT COUNT(*) as count FROM contact_requests
                    WHERE user_id = %s AND request_type = %s AND prescription_id = %s
                    AND status = 'pending'
                """
                cursor.execute(query, (user_id, request_type, prescription_id))
            else:
                query = """
                    SELECT COUNT(*) as count FROM contact_requests
                    WHERE user_id = %s AND request_type = %s AND status = 'pending'
                """
                cursor.execute(query, (user_id, request_type))

            result = cursor.fetchone()
            return result.get('count', 0) > 0

        except Exception as e:
            print(f"Error checking existing request: {e}")
            return False
