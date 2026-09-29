from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path

from neo4j import GraphDatabase

from backend.app.config import settings


ROOT = Path(__file__).resolve().parents[1]

OUTPUT_DIR = (
    ROOT
    / "data"
    / "processed"
    / "events"
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "temporal_coordination_findings.json"
)

WINDOW_SECONDS = 15 * 60
MIN_PARTICIPANTS = 3


def normalize_timestamp(value):
    if value is None:
        return None

    if hasattr(value, "to_native"):
        return value.to_native()

    if isinstance(value, str):
        return datetime.fromisoformat(value)

    return value


def main() -> None:

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

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

            result = session.run(
                """
                MATCH
                    (p:Person)-[r:SEEN_AT]->(l:Location)

                WHERE
                    r.timestamp IS NOT NULL

                RETURN
                    p.person_id AS person_id,
                    p.name AS person_name,
                    l.location_id AS location_id,
                    l.name AS location_name,
                    r.timestamp AS timestamp,
                    r.evidence_id AS evidence_id,
                    r.case_id AS case_id

                ORDER BY
                    l.location_id,
                    r.timestamp
                """
            )

            rows = [
                record.data()
                for record in result
            ]

        grouped = defaultdict(list)

        for row in rows:

            row["timestamp"] = (
                normalize_timestamp(
                    row["timestamp"]
                )
            )

            if row["timestamp"] is None:
                continue

            grouped[
                row["location_id"]
            ].append(row)

        findings = []

        for location_id, observations in (
            grouped.items()
        ):

            observations.sort(
                key=lambda item: item[
                    "timestamp"
                ]
            )

            for start_index in range(
                len(observations)
            ):

                start = observations[
                    start_index
                ]

                window = [start]

                for candidate in observations[
                    start_index + 1:
                ]:

                    elapsed = (
                        candidate[
                            "timestamp"
                        ]
                        - start["timestamp"]
                    ).total_seconds()

                    if elapsed > WINDOW_SECONDS:
                        break

                    window.append(
                        candidate
                    )

                # Only one observation per person
                # should count toward participants.
                people = {}

                for observation in window:

                    people[
                        observation[
                            "person_id"
                        ]
                    ] = observation

                if (
                    len(people)
                    < MIN_PARTICIPANTS
                ):
                    continue

                participants = sorted(
                    people.keys()
                )

                evidence_ids = sorted(
                    {
                        observation[
                            "evidence_id"
                        ]
                        for observation
                        in window
                        if observation[
                            "evidence_id"
                        ]
                    }
                )

                case_ids = sorted(
                    {
                        observation[
                            "case_id"
                        ]
                        for observation
                        in window
                        if observation[
                            "case_id"
                        ]
                    }
                )

                timestamps = [
                    observation[
                        "timestamp"
                    ]
                    for observation
                    in window
                ]

                window_start = min(timestamps)
                window_end = max(timestamps)

                window_seconds = int(
                    (
                        window_end
                        - window_start
                    ).total_seconds()
                )

                finding_id = (
                    f"TEMP-{location_id}-"
                    f"{window_start.isoformat()}"
                )

                findings.append(
                    {
                        "finding_id": finding_id,
                        "finding_type":
                            "TEMPORAL_COORDINATION",
                        "location_id": location_id,
                        "location_name":
                            start[
                                "location_name"
                            ],
                        "participants":
                            participants,
                        "participant_count":
                            len(participants),
                        "window_start":
                            window_start.isoformat(),
                        "window_end":
                            window_end.isoformat(),
                        "window_seconds":
                            window_seconds,
                        "evidence_ids":
                            evidence_ids,
                        "case_ids":
                            case_ids,
                        "method":
                            "co_location_window",
                        "parameters": {
                            "window_seconds":
                                WINDOW_SECONDS,
                            "min_participants":
                                MIN_PARTICIPANTS,
                        },
                    }
                )

        # Remove duplicates.
        unique_findings = {}

        for finding in findings:

            key = (
                finding["location_id"],
                tuple(
                    finding["participants"]
                ),
                finding["window_start"],
            )

            unique_findings[key] = finding

        final_findings = list(
            unique_findings.values()
        )

        with OUTPUT_PATH.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                final_findings,
                file,
                indent=2,
                ensure_ascii=False,
            )

        print(
            "Temporal coordination detection completed."
        )

        print(
            f"Findings generated: "
            f"{len(final_findings)}"
        )

        print(
            f"Output: {OUTPUT_PATH}"
        )

    finally:
        driver.close()


if __name__ == "__main__":
    main()