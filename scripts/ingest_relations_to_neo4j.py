from __future__ import annotations

import json
from pathlib import Path

from neo4j import GraphDatabase

from backend.app.config import settings


ROOT = Path(__file__).resolve().parents[1]

RELATION_PATH = (
    ROOT
    / "data"
    / "processed"
    / "relationships"
    / "report_relationships.json"
)

EVENT_PATH = (
    ROOT
    / "data"
    / "processed"
    / "events"
    / "report_events.json"
)


ALLOWED_RELATION_TYPES = {
    "ASSOCIATED_WITH",
    "SEEN_AT",
    "MEETS",
    "USES",
    "MENTIONED_IN",
}


ENTITY_CONFIG = {
    "Person": "person_id",
    "Organization": "organization_id",
    "Location": "location_id",
    "Vehicle": "vehicle_id",
    "Phone": "phone_id",
    "Evidence": "evidence_id",
}


def load_json(
    path: Path,
) -> list[dict]:

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


def create_relationship(
    session,
    relationship: dict,
) -> None:

    relation_type = relationship[
        "relation_type"
    ]

    if relation_type not in ALLOWED_RELATION_TYPES:
        raise ValueError(
            f"Unsupported relationship type: "
            f"{relation_type}"
        )

    subject_type = relationship[
        "subject_type"
    ]

    object_type = relationship[
        "object_type"
    ]

    subject_property = ENTITY_CONFIG[
        subject_type
    ]

    object_property = ENTITY_CONFIG[
        object_type
    ]

    query = f"""
    MATCH (subject:{subject_type} {{{subject_property}: $subject_id}})
    MATCH (object:{object_type} {{{object_property}: $object_id}})

    MERGE (subject)-[r:{relation_type} {{
        evidence_id: $evidence_id
    }}]->(object)

    SET r.case_id = $case_id,
        r.confidence = $confidence,
        r.extraction_method = $extraction_method,
        r.source_sentence = $source_sentence
    """

    session.run(
        query,
        subject_id=relationship[
            "subject_id"
        ],
        object_id=relationship[
            "object_id"
        ],
        evidence_id=relationship[
            "evidence_id"
        ],
        case_id=relationship[
            "case_id"
        ],
        confidence=relationship[
            "confidence"
        ],
        extraction_method=relationship[
            "extraction_method"
        ],
        source_sentence=relationship[
            "source_sentence"
        ],
    )


def create_event(
    session,
    event: dict,
) -> None:

    session.run(
        """
        MERGE (e:Event {
            event_id: $event_id
        })

        SET e.event_type = $event_type,
            e.case_id = $case_id,
            e.evidence_id = $evidence_id,
            e.timestamp =
                CASE
                    WHEN $timestamp IS NULL
                    THEN NULL
                    ELSE datetime($timestamp)
                END,
            e.time_precision = $time_precision,
            e.description = $description,
            e.relation_types = $relation_types
        """,
        event_id=event[
            "event_id"
        ],
        event_type=event[
            "event_type"
        ],
        case_id=event[
            "case_id"
        ],
        evidence_id=event[
            "evidence_id"
        ],
        timestamp=event[
            "timestamp"
        ],
        time_precision=event[
            "time_precision"
        ],
        description=event[
            "description"
        ],
        relation_types=event[
            "relation_types"
        ],
    )


def link_event_entities(
    session,
    event: dict,
) -> None:

    for entity in event[
        "entity_ids"
    ]:

        entity_type = entity[
            "entity_type"
        ]

        if entity_type not in ENTITY_CONFIG:
            continue

        property_name = ENTITY_CONFIG[
            entity_type
        ]

        query = f"""
        MATCH (entity:{entity_type}
              {{{property_name}: $entity_id}})

        MATCH (event:Event {{event_id: $event_id}})

        MERGE (entity)-[:INVOLVED_IN]->(event)
        """

        session.run(
            query,
            entity_id=entity[
                "entity_id"
            ],
            event_id=event[
                "event_id"
            ],
        )


def link_event_evidence(
    session,
    event: dict,
) -> None:

    session.run(
        """
        MATCH (event:Event {
            event_id: $event_id
        })

        MATCH (evidence:Evidence {
            evidence_id: $evidence_id
        })

        MERGE (event)-[:SUPPORTED_BY]->(evidence)
        """,
        event_id=event[
            "event_id"
        ],
        evidence_id=event[
            "evidence_id"
        ],
    )


def main() -> None:

    relationships = load_json(
        RELATION_PATH
    )

    events = load_json(
        EVENT_PATH
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

            for relationship in relationships:
                create_relationship(
                    session,
                    relationship,
                )

            for event in events:

                create_event(
                    session,
                    event,
                )

                link_event_entities(
                    session,
                    event,
                )

                link_event_evidence(
                    session,
                    event,
                )

        print(
            "Relations and events successfully "
            "ingested into Neo4j."
        )

        print(
            f"Relationships processed: "
            f"{len(relationships)}"
        )

        print(
            f"Events processed: {len(events)}"
        )

    finally:
        driver.close()


if __name__ == "__main__":
    main()