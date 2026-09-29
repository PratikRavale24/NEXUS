from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path

from neo4j import Driver


PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data"


def read_csv(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    with path.open(
        "r",
        newline="",
        encoding="utf-8",
    ) as file:
        return list(csv.DictReader(file))


def parse_int(value: str) -> int:
    return int(value)


def parse_float(value: str) -> float:
    return float(value)


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def load_master_entities(driver: Driver) -> None:
    persons = read_csv(DATA_DIR / "persons.csv")
    phones = read_csv(DATA_DIR / "phones.csv")
    vehicles = read_csv(DATA_DIR / "vehicles.csv")
    locations = read_csv(DATA_DIR / "locations.csv")
    organizations = read_csv(DATA_DIR / "organizations.csv")
    accounts = read_csv(DATA_DIR / "accounts.csv")

    with driver.session() as session:

        session.run(
            """
            UNWIND $rows AS row
            MERGE (p:Person {person_id: row.person_id})
            SET p.name = row.name,
                p.normalized_name = row.normalized_name
            """,
            rows=persons,
        )

        session.run(
            """
            UNWIND $rows AS row
            MERGE (p:Phone {phone_id: row.phone_id})
            SET p.normalized_number = row.phone_number
            """,
            rows=phones,
        )

        session.run(
            """
            UNWIND $rows AS row
            MERGE (v:Vehicle {vehicle_id: row.vehicle_id})
            SET v.registration = row.registration
            """,
            rows=vehicles,
        )

        session.run(
            """
            UNWIND $rows AS row
            MERGE (l:Location {location_id: row.location_id})
            SET l.name = row.name
            """,
            rows=locations,
        )

        session.run(
            """
            UNWIND $rows AS row
            MERGE (o:Organization {
                organization_id: row.organization_id
            })
            SET o.name = row.name
            """,
            rows=organizations,
        )

        session.run(
            """
            UNWIND $rows AS row
            MERGE (a:Account {account_id: row.account_id})
            SET a.account_number = row.account_number
            """,
            rows=accounts,
        )


def load_phone_ownership(driver: Driver) -> None:
    rows = read_csv(DATA_DIR / "phone_ownership.csv")

    with driver.session() as session:
        session.run(
            """
            UNWIND $rows AS row

            MATCH (p:Person {person_id: row.person_id})
            MATCH (ph:Phone {phone_id: row.phone_id})

            MERGE (p)-[r:OWNS]->(ph)

            SET r.source_id = row.source_id
            """,
            rows=rows,
        )


def load_account_ownership(driver: Driver) -> None:
    rows = read_csv(DATA_DIR / "account_ownership.csv")

    with driver.session() as session:
        session.run(
            """
            UNWIND $rows AS row

            MATCH (p:Person {person_id: row.person_id})
            MATCH (a:Account {account_id: row.account_id})

            MERGE (p)-[r:OWNS]->(a)

            SET r.source_id = row.source_id
            """,
            rows=rows,
        )


def load_cdr(driver: Driver) -> None:
    rows = read_csv(
        DATA_DIR / "raw" / "cdr" / "cdr.csv"
    )

    with driver.session() as session:

        prepared = []

        for row in rows:
            prepared.append(
                {
                    "cdr_id": row["cdr_id"],
                    "from_phone": row["from_phone"],
                    "to_phone": row["to_phone"],
                    "timestamp": parse_datetime(
                        row["timestamp"]
                    ).isoformat(),
                    "duration_seconds": parse_int(
                        row["duration_seconds"]
                    ),
                    "case_id": row["case_id"],
                }
            )

        session.run(
            """
            UNWIND $rows AS row

            MATCH (from:Phone {
                phone_id: row.from_phone
            })

            MATCH (to:Phone {
                phone_id: row.to_phone
            })

            MERGE (from)-[r:CALLS {
                evidence_id: row.cdr_id
            }]->(to)

            SET r.timestamp = datetime(row.timestamp),
                r.duration_seconds = row.duration_seconds,
                r.source_id = "CDR",
                r.case_id = row.case_id
            """,
            rows=prepared,
        )


def load_financial(driver: Driver) -> None:
    rows = read_csv(
        DATA_DIR
        / "raw"
        / "financial"
        / "transactions.csv"
    )

    with driver.session() as session:

        prepared = []

        for row in rows:
            prepared.append(
                {
                    "transaction_id": row["transaction_id"],
                    "from_account": row["from_account"],
                    "to_account": row["to_account"],
                    "amount": parse_float(row["amount"]),
                    "timestamp": parse_datetime(
                        row["timestamp"]
                    ).isoformat(),
                    "case_id": row["case_id"],
                }
            )

        session.run(
            """
            UNWIND $rows AS row

            MATCH (from:Account {
                account_id: row.from_account
            })

            MATCH (to:Account {
                account_id: row.to_account
            })

            MERGE (from)-[r:TRANSFERS_TO {
                evidence_id: row.transaction_id
            }]->(to)

            SET r.amount = row.amount,
                r.timestamp = datetime(row.timestamp),
                r.source_id = "BANK",
                r.case_id = row.case_id
            """,
            rows=prepared,
        )


def load_surveillance(driver: Driver) -> None:
    rows = read_csv(
        DATA_DIR
        / "raw"
        / "surveillance"
        / "surveillance.csv"
    )

    with driver.session() as session:

        prepared = []

        for row in rows:
            prepared.append(
                {
                    "surveillance_id": row[
                        "surveillance_id"
                    ],
                    "person_id": row["person_id"],
                    "vehicle_id": row["vehicle_id"],
                    "location_id": row["location_id"],
                    "timestamp": parse_datetime(
                        row["timestamp"]
                    ).isoformat(),
                    "case_id": row["case_id"],
                }
            )

        session.run(
            """
            UNWIND $rows AS row

            MATCH (p:Person {
                person_id: row.person_id
            })

            MATCH (v:Vehicle {
                vehicle_id: row.vehicle_id
            })

            MATCH (l:Location {
                location_id: row.location_id
            })

            MERGE (p)-[u:USES {
                evidence_id: row.surveillance_id
            }]->(v)

            SET u.timestamp = datetime(row.timestamp),
                u.source_id = "SURVEILLANCE",
                u.case_id = row.case_id

            MERGE (p)-[s:SEEN_AT {
                evidence_id: row.surveillance_id
            }]->(l)

            SET s.timestamp = datetime(row.timestamp),
                s.source_id = "SURVEILLANCE",
                s.case_id = row.case_id
            """,
            rows=prepared,
        )


def load_reports(driver: Driver) -> None:
    reports = read_csv(
        DATA_DIR
        / "raw"
        / "fir"
        / "reports.csv"
    )

    with driver.session() as session:
        session.run(
            """
            UNWIND $rows AS row

            MERGE (e:Evidence {
                evidence_id: row.document_id
            })

            SET e.document_type = row.document_type,
                e.case_id = row.case_id,
                e.text = row.text
            """,
            rows=reports,
        )


def run_ingestion(driver: Driver) -> None:
    load_master_entities(driver)
    load_phone_ownership(driver)
    load_account_ownership(driver)
    load_cdr(driver)
    load_financial(driver)
    load_surveillance(driver)
    load_reports(driver)