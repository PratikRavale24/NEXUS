from __future__ import annotations

import csv
import random
from datetime import datetime, timedelta
from pathlib import Path


SEED = 42
random.seed(SEED)

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

RAW_DIR = DATA_DIR / "raw"
GT_DIR = DATA_DIR / "ground_truth"


# --------------------------------------------------
# Configuration
# --------------------------------------------------

NUM_PERSONS = 25
NUM_PHONES = 30
NUM_VEHICLES = 10
NUM_LOCATIONS = 10
NUM_ORGANIZATIONS = 5
NUM_ACCOUNTS = 20

START_DATE = datetime(2026, 8, 1)


# --------------------------------------------------
# Utility functions
# --------------------------------------------------

def ensure_directories() -> None:
    directories = [
        RAW_DIR / "cdr",
        RAW_DIR / "financial",
        RAW_DIR / "surveillance",
        RAW_DIR / "fir",
        RAW_DIR / "reports",
        GT_DIR / "entity_matches",
        GT_DIR / "relationships",
        GT_DIR / "anomalies",
        GT_DIR / "communities",
        GT_DIR / "key_nodes",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)


def random_timestamp() -> str:
    offset_days = random.randint(0, 29)
    offset_minutes = random.randint(0, 23 * 60 + 59)

    timestamp = START_DATE + timedelta(
        days=offset_days,
        minutes=offset_minutes,
    )

    return timestamp.isoformat()


# --------------------------------------------------
# Master entities
# --------------------------------------------------

FIRST_NAMES = [
    "Rohan",
    "Arjun",
    "Amit",
    "Neha",
    "Karan",
    "Vikram",
    "Priya",
    "Rahul",
    "Sahil",
    "Ananya",
    "Nikhil",
    "Meera",
    "Aditya",
    "Isha",
    "Manav",
]

LAST_NAMES = [
    "Patil",
    "Mehta",
    "Shah",
    "Verma",
    "Kulkarni",
    "Joshi",
    "Deshmukh",
    "Pawar",
]


def generate_people() -> list[dict]:
    people = []

    for index in range(1, NUM_PERSONS + 1):
        first = FIRST_NAMES[(index - 1) % len(FIRST_NAMES)]
        last = LAST_NAMES[(index - 1) % len(LAST_NAMES)]

        name = f"{first} {last}"

        people.append(
            {
                "person_id": f"P{index:03d}",
                "name": name,
                "normalized_name": name.lower(),
            }
        )

    return people


def generate_phones() -> list[dict]:
    phones = []

    for index in range(1, NUM_PHONES + 1):
        phones.append(
            {
                "phone_id": f"PH{index:03d}",
                "phone_number": f"91987654{index:04d}",
            }
        )

    return phones


def generate_vehicles() -> list[dict]:
    vehicles = []

    for index in range(1, NUM_VEHICLES + 1):
        vehicles.append(
            {
                "vehicle_id": f"V{index:03d}",
                "registration": f"MH01XX{1000 + index}",
            }
        )

    return vehicles


def generate_locations() -> list[dict]:
    names = [
        "Central Market",
        "North Railway Station",
        "Riverside Warehouse",
        "City Bus Depot",
        "East Industrial Area",
        "Central Mall",
        "Harbor Road",
        "Old Highway Junction",
        "West Logistics Hub",
        "Metro Parking Area",
    ]

    return [
        {
            "location_id": f"L{index:03d}",
            "name": name,
        }
        for index, name in enumerate(names, start=1)
    ]


def generate_organizations() -> list[dict]:
    names = [
        "Alpha Traders",
        "Vertex Logistics",
        "Metro Supplies",
        "Orion Exports",
        "Prime Services",
    ]

    return [
        {
            "organization_id": f"ORG{index:03d}",
            "name": name,
        }
        for index, name in enumerate(names, start=1)
    ]


def generate_accounts() -> list[dict]:
    accounts = []

    for index in range(1, NUM_ACCOUNTS + 1):
        accounts.append(
            {
                "account_id": f"ACC{index:03d}",
                "account_number": f"SYNTH{index:08d}",
            }
        )

    return accounts


# --------------------------------------------------
# Ownership mappings
# --------------------------------------------------

def generate_phone_ownership(people: list[dict], phones: list[dict]) -> list[dict]:
    ownership = []

    for index, phone in enumerate(phones):
        person = people[index % len(people)]

        ownership.append(
            {
                "person_id": person["person_id"],
                "phone_id": phone["phone_id"],
                "source_id": "MASTER-001",
            }
        )

    # Deliberate shared phone relationship
    ownership.append(
        {
            "person_id": "P005",
            "phone_id": "PH025",
            "source_id": "INTEL-004",
        }
    )

    return ownership


def generate_account_ownership(
    people: list[dict],
    accounts: list[dict],
) -> list[dict]:
    ownership = []

    for index, account in enumerate(accounts):
        person = people[index % len(people)]

        ownership.append(
            {
                "person_id": person["person_id"],
                "account_id": account["account_id"],
                "source_id": "BANK-001",
            }
        )

    return ownership


# --------------------------------------------------
# CDR generation
# --------------------------------------------------

def generate_cdr() -> list[dict]:
    rows = []

    # Normal background communications
    for index in range(180):
        from_phone = random.randint(1, NUM_PHONES)
        to_phone = random.randint(1, NUM_PHONES)

        if from_phone == to_phone:
            continue

        rows.append(
            {
                "cdr_id": f"CDR-{index + 1:04d}",
                "from_phone": f"PH{from_phone:03d}",
                "to_phone": f"PH{to_phone:03d}",
                "timestamp": random_timestamp(),
                "duration_seconds": random.randint(30, 900),
                "case_id": "CASE-001",
            }
        )

    # Planted high-connectivity communication node: PH005
    cdr_id = 1000

    for target in range(1, 16):
        if target == 5:
            continue

        cdr_id += 1

        rows.append(
            {
                "cdr_id": f"CDR-{cdr_id:04d}",
                "from_phone": "PH005",
                "to_phone": f"PH{target:03d}",
                "timestamp": random_timestamp(),
                "duration_seconds": random.randint(120, 900),
                "case_id": "CASE-001",
            }
        )

    # Planted temporal coordination burst
    coordinated_time = datetime(2026, 8, 18, 20, 30)

    for index, phone in enumerate(
        ["PH005", "PH009", "PH011", "PH014"]
    ):
        rows.append(
            {
                "cdr_id": f"CDR-TEMP-{index + 1:03d}",
                "from_phone": phone,
                "to_phone": "PH020",
                "timestamp": (
                    coordinated_time + timedelta(minutes=index * 4)
                ).isoformat(),
                "duration_seconds": 300 + index * 20,
                "case_id": "CASE-001",
            }
        )

    return rows


# --------------------------------------------------
# Financial transactions
# --------------------------------------------------

def generate_financial() -> list[dict]:
    rows = []

    for index in range(100):
        sender = random.randint(1, NUM_ACCOUNTS)
        receiver = random.randint(1, NUM_ACCOUNTS)

        if sender == receiver:
            continue

        rows.append(
            {
                "transaction_id": f"TXN-{index + 1:04d}",
                "from_account": f"ACC{sender:03d}",
                "to_account": f"ACC{receiver:03d}",
                "amount": random.randint(500, 50000),
                "timestamp": random_timestamp(),
                "case_id": "CASE-001",
            }
        )

    # Coordinated financial activity
    for index in range(8):
        rows.append(
            {
                "transaction_id": f"TXN-COORD-{index + 1:03d}",
                "from_account": "ACC005",
                "to_account": f"ACC{10 + index:03d}",
                "amount": 25000 + index * 1500,
                "timestamp": (
                    datetime(2026, 8, 19, 10, 0)
                    + timedelta(minutes=index * 10)
                ).isoformat(),
                "case_id": "CASE-001",
            }
        )

    return rows


# --------------------------------------------------
# Surveillance
# --------------------------------------------------

def generate_surveillance() -> list[dict]:
    rows = []

    for index in range(80):
        rows.append(
            {
                "surveillance_id": f"SURV-{index + 1:04d}",
                "person_id": f"P{random.randint(1, NUM_PERSONS):03d}",
                "vehicle_id": f"V{random.randint(1, NUM_VEHICLES):03d}",
                "location_id": f"L{random.randint(1, NUM_LOCATIONS):03d}",
                "timestamp": random_timestamp(),
                "case_id": "CASE-001",
            }
        )

    # Planted coordinated meeting
    coordinated_time = datetime(2026, 8, 18, 21, 0)

    for index, person_id in enumerate(
        ["P005", "P009", "P011", "P014"]
    ):
        rows.append(
            {
                "surveillance_id": f"SURV-COORD-{index + 1:03d}",
                "person_id": person_id,
                "vehicle_id": "V005",
                "location_id": "L003",
                "timestamp": (
                    coordinated_time
                    + timedelta(minutes=index * 3)
                ).isoformat(),
                "case_id": "CASE-001",
            }
        )

    return rows


# --------------------------------------------------
# FIR / reports
# --------------------------------------------------

def generate_reports() -> tuple[list[dict], list[dict]]:
    documents = [
        {
            "document_id": "FIR-001",
            "document_type": "FIR",
            "case_id": "CASE-001",
            "text": (
                "On 12 August 2026, Rohan Patil was observed near "
                "Central Market with Amit Verma. Vehicle MH01XX1005 "
                "was seen at the location."
            ),
        },
        {
            "document_id": "FIR-002",
            "document_type": "REPORT",
            "case_id": "CASE-001",
            "text": (
                "Rohan K. Patil was seen communicating with a number "
                "associated with Alpha Traders."
            ),
        },
        {
            "document_id": "FIR-003",
            "document_type": "SURVEILLANCE_REPORT",
            "case_id": "CASE-001",
            "text": (
                "R. Patil and Karan Shah were observed near Riverside "
                "Warehouse on 18 August 2026."
            ),
        },
        {
            "document_id": "FIR-004",
            "document_type": "INTELLIGENCE_REPORT",
            "case_id": "CASE-001",
            "text": (
                "Amit Verma was reported near Vehicle MH01XX1005 "
                "during an evening meeting."
            ),
        },
    ]

    ground_truth = [
        {
            "document_id": "FIR-001",
            "mention": "Rohan Patil",
            "entity_type": "Person",
            "canonical_id": "P001",
        },
        {
            "document_id": "FIR-001",
            "mention": "Amit Verma",
            "entity_type": "Person",
            "canonical_id": "P002",
        },
        {
            "document_id": "FIR-002",
            "mention": "Rohan K. Patil",
            "entity_type": "Person",
            "canonical_id": "P001",
        },
        {
            "document_id": "FIR-003",
            "mention": "R. Patil",
            "entity_type": "Person",
            "canonical_id": "P001",
        },
        {
            "document_id": "FIR-003",
            "mention": "Karan Shah",
            "entity_type": "Person",
            "canonical_id": "P003",
        },
    ]

    return documents, ground_truth


# --------------------------------------------------
# Ground truth
# --------------------------------------------------

def generate_ground_truth() -> None:
    write_csv(
        GT_DIR / "key_nodes" / "key_nodes.csv",
        [
            {
                "node_type": "Person",
                "node_id": "P005",
                "role": "central_node",
                "reason": "High planted connectivity",
            },
            {
                "node_type": "Person",
                "node_id": "P009",
                "role": "bridge_node",
                "reason": "Connects two planted groups",
            },
        ],
    )

    write_csv(
        GT_DIR / "anomalies" / "anomalies.csv",
        [
            {
                "entity_id": "PH005",
                "anomaly_type": "communication_burst",
                "description": (
                    "Sudden increase in communication with many "
                    "previously uncommon contacts."
                ),
            }
        ],
    )

    write_csv(
        GT_DIR / "communities" / "communities.csv",
        [
            {
                "community_id": "C01",
                "members": "P001,P002,P005,P011,P014",
            },
            {
                "community_id": "C02",
                "members": "P009,P015,P017,P019",
            },
        ],
    )


# --------------------------------------------------
# Main
# --------------------------------------------------

def main() -> None:
    ensure_directories()

    people = generate_people()
    phones = generate_phones()
    vehicles = generate_vehicles()
    locations = generate_locations()
    organizations = generate_organizations()
    accounts = generate_accounts()

    write_csv(DATA_DIR / "persons.csv", people)
    write_csv(DATA_DIR / "phones.csv", phones)
    write_csv(DATA_DIR / "vehicles.csv", vehicles)
    write_csv(DATA_DIR / "locations.csv", locations)
    write_csv(DATA_DIR / "organizations.csv", organizations)
    write_csv(DATA_DIR / "accounts.csv", accounts)

    write_csv(
        DATA_DIR / "phone_ownership.csv",
        generate_phone_ownership(people, phones),
    )

    write_csv(
        DATA_DIR / "account_ownership.csv",
        generate_account_ownership(people, accounts),
    )

    write_csv(
        RAW_DIR / "cdr" / "cdr.csv",
        generate_cdr(),
    )

    write_csv(
        RAW_DIR / "financial" / "transactions.csv",
        generate_financial(),
    )

    write_csv(
        RAW_DIR / "surveillance" / "surveillance.csv",
        generate_surveillance(),
    )

    reports, entity_ground_truth = generate_reports()

    write_csv(
        RAW_DIR / "fir" / "reports.csv",
        reports,
    )

    write_csv(
        GT_DIR / "entity_matches" / "report_entity_gold.csv",
        entity_ground_truth,
    )

    generate_ground_truth()

    print("Synthetic NEXUS dataset generated successfully.")


if __name__ == "__main__":
    main()