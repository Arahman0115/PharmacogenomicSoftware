"""PharmGKB API integration for drug-gene interaction lookup"""
import requests
from typing import List, Dict, Tuple
from datetime import datetime


class PharmGKBService:
    """Service for calling PharmGKB API and processing variant annotations"""

    BASE_URL = "https://api.pharmgkb.org/v1/data"
    HEADERS = {"accept": "application/json"}

    # Score threshold for determining risk level
    SCORE_THRESHOLDS = {
        "High": 4,
        "Moderate": 2,
        "Low": 0
    }

    @staticmethod
    def get_variant_annotations(variant_id: str) -> Tuple[List[Dict], bool]:
        """
        Fetch variant annotations from PharmGKB by variant fingerprint/rs number

        Args:
            variant_id: The variant fingerprint or rs number (e.g., 'rs4149056')

        Returns:
            Tuple of (medication_conflicts, success)
            medication_conflicts: List of dicts with medication name and risk info
            success: Boolean indicating if API call succeeded
        """
        try:
            # Construct URL with variant fingerprint
            url = f"{PharmGKBService.BASE_URL}/variantAnnotation?location.fingerprint={variant_id}&view=full"

            response = requests.get(url, headers=PharmGKBService.HEADERS, timeout=10)

            if response.status_code != 200:
                print(f"PharmGKB API error: {response.status_code}")
                return [], False

            data = response.json().get("data", [])
            medication_conflicts = []

            # Process each annotation
            for annotation in data:
                score = annotation.get("score", 0)

                # Only include if score is meaningful (Low = 0, Moderate = 2, High = 4+)
                if score >= 0:
                    risk_level = PharmGKBService._determine_risk_level(score)
                    sentence = annotation.get("sentence", "")

                    # Extract related chemicals/medications
                    related_chemicals = annotation.get("relatedChemicals", [])

                    for chemical in related_chemicals:
                        medication_conflicts.append({
                            "medication_name": chemical.get("name", "Unknown"),
                            "risk_level": risk_level,
                            "score": score,
                            "sentence": sentence,
                            "pgkb_url": chemical.get("url", "")
                        })

            return medication_conflicts, True

        except requests.exceptions.RequestException as e:
            print(f"PharmGKB API request failed: {e}")
            return [], False
        except Exception as e:
            print(f"Error processing PharmGKB response: {e}")
            return [], False

    @staticmethod
    def get_gene_label_interactions(gene_symbol: str) -> Tuple[List[str], bool]:
        """
        Fetch medication labels related to a gene from PharmGKB

        Args:
            gene_symbol: Gene symbol (e.g., 'SLCO1B1')

        Returns:
            Tuple of (medication_names, success)
        """
        try:
            url = f"{PharmGKBService.BASE_URL}/label?relatedGenes.symbol={gene_symbol}"

            response = requests.get(url, headers=PharmGKBService.HEADERS, timeout=10)

            if response.status_code != 200:
                print(f"PharmGKB label API error: {response.status_code}")
                return [], False

            data = response.json().get("data", [])
            medication_names = set()

            for item in data:
                related_chemicals = item.get("relatedChemicals", [])
                for chemical in related_chemicals:
                    if "name" in chemical:
                        medication_names.add(chemical["name"])

            return list(medication_names), True

        except Exception as e:
            print(f"Error fetching gene labels: {e}")
            return [], False

    @staticmethod
    def _determine_risk_level(score: int) -> str:
        """Determine risk level based on PharmGKB score"""
        if score >= PharmGKBService.SCORE_THRESHOLDS["High"]:
            return "High"
        elif score >= PharmGKBService.SCORE_THRESHOLDS["Moderate"]:
            return "Moderate"
        else:
            return "Low"

    @staticmethod
    def save_variant_conflicts_to_db(db_connection, user_id: int, gene: str,
                                      variant: str, genotype: str,
                                      medication_conflicts: List[Dict]) -> bool:
        """
        Save variant and its medication conflicts to the database

        Args:
            db_connection: Database connection object
            user_id: Patient user ID
            gene: Gene name
            variant: Variant identifier
            genotype: Genotype
            medication_conflicts: List of medication conflict dicts from API

        Returns:
            Success boolean
        """
        try:
            cursor = db_connection.cursor

            # Insert into final_genetic_info
            insert_genetic = """
                INSERT INTO final_genetic_info
                (user_id, gene, variant, genotype, date_tested, test_result)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE date_tested = %s
            """
            today = datetime.now().strftime('%Y-%m-%d')
            test_result = f"Variant {variant} tested via PharmGKB"

            cursor.execute(insert_genetic, (
                user_id, gene, variant, genotype, today, test_result, today
            ))

            # Get the genetic_info_id for reference
            genetic_id = cursor.lastrowid

            # Insert medication conflicts into drug_review table
            insert_conflicts = """
                INSERT INTO drug_review
                (user_id, medication_id, gene, variant, risk_level, notes, status)
                SELECT %s, m.medication_id, %s, %s, %s, %s, 'active'
                FROM medications m
                WHERE m.medication_name = %s
                ON DUPLICATE KEY UPDATE
                    risk_level = VALUES(risk_level),
                    notes = VALUES(notes),
                    status = 'active'
            """

            for conflict in medication_conflicts:
                notes = f"Score: {conflict['score']} - {conflict['sentence']}"
                cursor.execute(insert_conflicts, (
                    user_id,
                    gene,
                    variant,
                    conflict["risk_level"],
                    notes,
                    conflict["medication_name"]
                ))

            db_connection.connection.commit()
            return True

        except Exception as e:
            print(f"Error saving variant conflicts to database: {e}")
            db_connection.connection.rollback()
            return False
