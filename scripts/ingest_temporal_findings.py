from __future__ import annotations

import json
from pathlib import Path

from neo4j import GraphDatabase

from backend.app.config import settings


ROOT = Path(__file__).resolve().parents[1]

FINDINGS_PATH = (
    ROOT
    / "data"
    / "processed"
    / "events"
    / "temporal_coordination_findings.json"
)


def main() -> None:

    with FINDINGS_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:

        findings = json.load(file)

    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(
            settings.neo4j_user,
            settings.neo4j_password,
        ),
    )

    try:

        driver.verify_connectivity()

        with driver.session() as session:

            for finding in findings:

                reasons = [
                    (
                        f"{finding['participant_count']} participants "
                        f"were observed within a "
                        f"{finding['window_seconds']}-second window."
                    ),
                    (
                        f"Location: "
                        f"{finding['location_name']}."
                    ),
                    (
                        f"Participants: "
                        f"{', '.join(finding['participants'])}."
                    ),
                ]

                description = (
                    f"{finding['participant_count']} participants "
                    f"were observed at "
                    f"{finding['location_name']} within "
                    f"{finding['window_seconds']} seconds."
                )

                session.run(
                    """
                    MERGE (
                        f:Finding {
                            finding_id: $finding_id
                        }
                    )

                    SET
                        f.finding_type = $finding_type,
                        f.description = $description,
                        f.reasons = $reasons,
                        f.location_id = $location_id,
                        f.location_name = $location_name,
                        f.participant_count = $participant_count,
                        f.participants = $participants,
                        f.window_start = datetime($window_start),
                        f.window_end = datetime($window_end),
                        f.window_seconds = $window_seconds,
                        f.evidence_ids = $evidence_ids,
                        f.case_ids = $case_ids,
                        f.method = $method,
                        f.status = "NEW"
                    """,
                    finding_id=finding["finding_id"],
                    finding_type=finding["finding_type"],
                    description=description,
                    reasons=reasons,
                    location_id=finding["location_id"],
                    location_name=finding["location_name"],
                    participant_count=finding["participant_count"],
                    participants=finding["participants"],
                    window_start=finding["window_start"],
                    window_end=finding["window_end"],
                    window_seconds=finding["window_seconds"],
                    evidence_ids=finding["evidence_ids"],
                    case_ids=finding["case_ids"],
                    method=finding["method"],
                )

                for person_id in finding["participants"]:

                    session.run(
                        """
                        MATCH (
                            f:Finding {
                                finding_id:
                                    $finding_id
                            }
                        )

                        MATCH (
                            p:Person {
                                person_id:
                                    $person_id
                            }
                        )

                        MERGE (
                            p)-[:PARTICIPANT_IN]->(f)
                        """,
                        finding_id=finding[
                            "finding_id"
                        ],
                        person_id=person_id,
                    )   

                for evidence_id in finding[
                    "evidence_ids"
                ]:

                    session.run(
                        """
                        MATCH (
                            f:Finding {
                                finding_id:
                                    $finding_id
                            }
                        )

                        MATCH (
                            e:Evidence {
                                evidence_id:
                                    $evidence_id
                            }
                        )

                        MERGE (
                            f)-[:SUPPORTED_BY]->(e)
                        """,
                        finding_id=finding[
                            "finding_id"
                        ],
                        evidence_id=evidence_id,
                    )

        print(
            "Temporal findings written to Neo4j."
        )

    finally:
        driver.close()


if __name__ == "__main__":
    main()