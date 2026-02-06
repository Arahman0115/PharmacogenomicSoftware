"""
Seed script - populates the new patient info and insurance fields
with realistic pharmacy patient data for all existing patients.

Usage:
    source pharmguienv/bin/activate
    python seed_patient_data.py
"""
import random
from DataBaseConnection import db_connection

# ── Realistic data pools ─────────────────────────────────────

GENDERS = ["Male", "Female", "Male", "Female", "Non-Binary"]

ETHNICITIES = [
    "White", "Black or African American", "Hispanic or Latino",
    "Asian", "Native American", "Pacific Islander", "Two or More Races"
]

LANGUAGES = [
    "English", "English", "English", "English", "English",
    "Spanish", "Spanish", "French", "Mandarin", "Vietnamese"
]

STREETS_2 = ["", "", "", "Apt 2B", "Suite 100", "Unit 4", "Floor 3", "Apt 12A"]

CITIES = [
    "Brooklyn", "Queens", "Manhattan", "Bronx", "Staten Island",
    "Jersey City", "Newark", "Yonkers", "New Rochelle", "Hoboken"
]

STATES = ["NY", "NY", "NY", "NY", "NY", "NJ", "NJ", "NY", "NY", "NJ"]

ZIP_CODES = [
    "11201", "11375", "10001", "10451", "10301",
    "07302", "07102", "10701", "10801", "07030"
]

CELL_PREFIXES = ["917", "646", "347", "929", "718"]
WORK_PREFIXES = ["212", "718", "516", "914", "201"]

EMERGENCY_FIRST = [
    "Maria", "James", "Linda", "Robert", "Patricia",
    "Michael", "Jennifer", "David", "Sarah", "Thomas"
]
EMERGENCY_LAST = [
    "Johnson", "Williams", "Brown", "Jones", "Garcia",
    "Miller", "Davis", "Rodriguez", "Martinez", "Anderson"
]

LOCATIONS = [
    "Main St Pharmacy", "Downtown Branch", "Eastside Location",
    "Westside Pharmacy", "Central Pharmacy", "North Plaza"
]

# Insurance data pools
PLAN_NAMES = [
    "Blue Cross Blue Shield PPO", "Aetna Choice POS II",
    "UnitedHealthcare Choice Plus", "Cigna Open Access Plus",
    "Empire BlueCross EPO", "Oscar Health Silver",
    "Humana Gold Plus", "Anthem Blue Preferred",
    "Molina Healthcare", "Fidelis Care"
]

PROVIDERS = [
    "Blue Cross Blue Shield", "Aetna", "UnitedHealthcare",
    "Cigna", "Empire BlueCross", "Oscar Health",
    "Humana", "Anthem", "Molina Healthcare", "Fidelis Care"
]

BINS = ["004336", "610014", "003858", "600428", "015905", "610279"]
PCNS = ["ADV", "MEDDPRIME", "9999", "MCAIDADV", "GHP", "ACE"]

PLAN_TYPES = [
    "Commercial", "Commercial", "Commercial", "Commercial",
    "Medicare Part D", "Medicaid", "Commercial"
]

RELATIONSHIP_CODES = ["01", "02", "03", "01", "01"]  # 01=cardholder, 02=spouse, 03=child


def random_phone(prefixes):
    prefix = random.choice(prefixes)
    return f"({prefix}) {random.randint(200,999)}-{random.randint(1000,9999)}"


def seed_patient_info(cursor, patients):
    """Populate new demographic fields for each patient"""
    print(f"\nSeeding patient info for {len(patients)} patients...")

    for i, pt in enumerate(patients):
        uid = pt['user_id']
        city_idx = i % len(CITIES)

        cursor.execute("""
            UPDATE patientsinfo SET
                gender = %s,
                race_ethnicity = %s,
                language = %s,
                address_2 = %s,
                city = COALESCE(NULLIF(city, ''), %s),
                state = COALESCE(NULLIF(state, ''), %s),
                zip_code = %s,
                cell_phone = %s,
                work_phone = %s,
                email = COALESCE(NULLIF(email, ''), %s),
                emergency_contact_name = %s,
                emergency_contact_phone = %s,
                preferred_location = %s,
                child_resistant_caps = %s,
                generic_substitution = %s,
                large_print_labels = %s
            WHERE user_id = %s
        """, (
            random.choice(GENDERS),
            random.choice(ETHNICITIES),
            random.choice(LANGUAGES),
            random.choice(STREETS_2),
            CITIES[city_idx],
            STATES[city_idx],
            ZIP_CODES[city_idx],
            random_phone(CELL_PREFIXES),
            random_phone(WORK_PREFIXES),
            f"{pt.get('first_name', 'patient').lower()}.{pt.get('last_name', 'user').lower()}@email.com",
            f"{random.choice(EMERGENCY_FIRST)} {random.choice(EMERGENCY_LAST)}",
            random_phone(CELL_PREFIXES),
            random.choice(LOCATIONS),
            random.choice([1, 1, 1, 0]),        # most want child-resistant
            random.choice([1, 1, 1, 0]),         # most allow generic sub
            random.choice([0, 0, 0, 0, 1]),      # few need large print
            uid
        ))
        print(f"  [{i+1}/{len(patients)}] {pt.get('first_name', '')} {pt.get('last_name', '')} - done")


def seed_insurance(cursor, patients):
    """Create insurance records for each patient"""
    print(f"\nSeeding insurance for {len(patients)} patients...")

    for i, pt in enumerate(patients):
        uid = pt['user_id']
        plan_idx = i % len(PLAN_NAMES)

        group_num = f"{random.randint(100000, 999999)}"
        cardholder = f"{pt.get('last_name', 'USER')[:3].upper()}{random.randint(100000000, 999999999)}"
        person_code = random.choice(["01", "02", "03"])
        policy_num = f"POL-{random.randint(10000000, 99999999)}"
        member_id = f"MEM-{random.randint(1000000, 9999999)}"

        eff_year = random.choice([2023, 2024, 2025])
        eff_month = random.randint(1, 12)
        exp_year = eff_year + random.choice([1, 2])

        copay_generic = random.choice([5.00, 10.00, 15.00, 20.00])
        copay_brand = random.choice([25.00, 35.00, 50.00, 75.00])

        # Use INSERT ... ON DUPLICATE KEY UPDATE so it's idempotent
        cursor.execute("""
            INSERT INTO patient_insurance
            (user_id, plan_name, insurance_provider, bin_number, pcn,
             group_number, cardholder_id, person_code, relationship_code,
             policy_number, member_id, plan_type,
             effective_date, expiration_date,
             copay_generic, copay_brand)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                plan_name = VALUES(plan_name),
                insurance_provider = VALUES(insurance_provider),
                bin_number = VALUES(bin_number),
                pcn = VALUES(pcn),
                group_number = VALUES(group_number),
                cardholder_id = VALUES(cardholder_id),
                person_code = VALUES(person_code),
                relationship_code = VALUES(relationship_code),
                policy_number = VALUES(policy_number),
                member_id = VALUES(member_id),
                plan_type = VALUES(plan_type),
                effective_date = VALUES(effective_date),
                expiration_date = VALUES(expiration_date),
                copay_generic = VALUES(copay_generic),
                copay_brand = VALUES(copay_brand)
        """, (
            uid,
            PLAN_NAMES[plan_idx],
            PROVIDERS[plan_idx],
            random.choice(BINS),
            random.choice(PCNS),
            group_num,
            cardholder,
            person_code,
            random.choice(RELATIONSHIP_CODES),
            policy_num,
            member_id,
            random.choice(PLAN_TYPES),
            f"{eff_year}-{eff_month:02d}-01",
            f"{exp_year}-{eff_month:02d}-01",
            copay_generic,
            copay_brand
        ))
        print(f"  [{i+1}/{len(patients)}] {pt.get('first_name', '')} {pt.get('last_name', '')} - insured")


def main():
    cursor = db_connection.cursor

    # Get all existing patients
    cursor.execute("SELECT user_id, first_name, last_name FROM patientsinfo")
    patients = cursor.fetchall()

    if not patients:
        print("No patients found in patientsinfo table.")
        return

    print(f"Found {len(patients)} patients to seed.")

    seed_patient_info(cursor, patients)
    seed_insurance(cursor, patients)

    db_connection.connection.commit()
    print(f"\nDone! Seeded {len(patients)} patients with demographics + insurance data.")


if __name__ == "__main__":
    main()
