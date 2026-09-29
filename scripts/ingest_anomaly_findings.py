from __future__ import annotations

import json
from pathlib import Path

from neo4j import GraphDatabase

from backend.app.config import settings


ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    ROOT
    / "data"
    / "processed"
    / "anomalies"
    / "anomaly_explanations.json"
)


def main() -> None:

    with INPUT_PATH.open(
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

            for item in findings:

                finding_id = (
                    f"ANOM-{item['person_id']}"
                )

                description = " ".join(
                    item["reasons"]
                )

                session.run(
                    """
                    MATCH (
                        p:Person {
                            person_id:
                                $person_id
                        }
                    )

                    MERGE (
                        f:Finding {
                            finding_id:
                                $finding_id
                        }
                    )

                    SET
                        f.finding_type =
                            "ANOMALY",
                        f.description =
                            $description,
                        f.anomaly_score =
                            $anomaly_score,
                        f.model =
                            $model,
                        f.status =
                            "NEW"

                    MERGE (
                        p)-[:SUBJECT_OF]->(f)
                    """,
                    person_id=item[
                        "person_id"
                    ],
                    finding_id=finding_id,
                    description=description,
                    anomaly_score=item[
                        "anomaly_score"
                    ],
                    model=item[
                        "model"
                    ],
                )

                # Connect the finding to the
                # person's relevant evidence.
                                # Collect supporting CDR evidence for the
                # person being analysed.
                evidence_result = session.run(
                    """
                    MATCH
                        (p:Person {
                            person_id: $person_id
                        })
                        -[:OWNS]->(ph:Phone)
                        -[c:CALLS]->()

                    WHERE
                        c.evidence_id IS NOT NULL

                    RETURN collect(
                        DISTINCT c.evidence_id
                    )[0..20] AS evidence_ids
                    """,
                    person_id=item["person_id"],
                )

                evidence_record = (
                    evidence_result.single()
                )

                evidence_ids = (
                    evidence_record["evidence_ids"]
                    if evidence_record
                    else []
                )

                description = " ".join(
                    item["reasons"]
                )

                session.run(
                    """
                    MATCH (
                        p:Person {
                            person_id: $person_id
                        }
                    )

                    MERGE (
                        f:Finding {
                            finding_id: $finding_id
                        }
                    )

                    SET
                        f.finding_type = "ANOMALY",
                        f.description = $description,
                        f.reasons = $reasons,
                        f.anomaly_score =
                            $anomaly_score,
                        f.model = $model,
                        f.evidence_ids =
                            $evidence_ids,
                        f.status = "NEW"

                    MERGE (
                        p)-[:SUBJECT_OF]->(f)
                    """,
                    person_id=item[
                        "person_id"
                    ],
                    finding_id=finding_id,
                    description=description,
                    reasons=item["reasons"],
                    anomaly_score=item[
                        "anomaly_score"
                    ],
                    model=item["model"],
                    evidence_ids=evidence_ids,
                )

        print(
            "Anomaly findings written to Neo4j."
        )

        print(
            f"Findings processed: "
            f"{len(findings)}"
        )

    finally:
        driver.close()


if __name__ == "__main__":
    main()