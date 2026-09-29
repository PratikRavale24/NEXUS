from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from backend.app.services.relation_extraction import (
    extract_report_relations,
    load_catalogs,
)


ROOT = Path(__file__).resolve().parents[1]

REPORT_PATH = (
    ROOT
    / "data"
    / "raw"
    / "fir"
    / "reports.csv"
)

ENTITY_PATH = (
    ROOT
    / "data"
    / "processed"
    / "entities"
    / "report_entity_mentions.json"
)

RELATION_DIR = (
    ROOT
    / "data"
    / "processed"
    / "relationships"
)

EVENT_DIR = (
    ROOT
    / "data"
    / "processed"
    / "events"
)

RELATION_PATH = (
    RELATION_DIR
    / "report_relationships.json"
)

EVENT_PATH = (
    EVENT_DIR
    / "report_events.json"
)


def main() -> None:

    RELATION_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    EVENT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    reports = pd.read_csv(
        REPORT_PATH
    ).to_dict("records")

    with ENTITY_PATH.open(
        "r",
        encoding="utf-8",
    ) as file:
        extracted_entities = json.load(file)

    catalogs = load_catalogs()

    all_relationships = []
    all_events = []

    for report in reports:

        report_entities = [
            entity
            for entity in extracted_entities
            if entity["document_id"]
            == report["document_id"]
        ]

        relationships, events = (
            extract_report_relations(
                report,
                report_entities,
                catalogs,
            )
        )

        all_relationships.extend(
            relationships
        )

        all_events.extend(
            events
        )

    with RELATION_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            all_relationships,
            file,
            indent=2,
            ensure_ascii=False,
        )

    with EVENT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            all_events,
            file,
            indent=2,
            ensure_ascii=False,
        )

    semantic_count = sum(
        1
        for relationship in all_relationships
        if relationship["relation_type"]
        != "MENTIONED_IN"
    )

    print(
        "NEXUS relation and event pipeline completed."
    )

    print(
        f"Total relationships: "
        f"{len(all_relationships)}"
    )

    print(
        f"Semantic relationships: "
        f"{semantic_count}"
    )

    print(
        f"Events: {len(all_events)}"
    )

    print(
        f"Relationships output: "
        f"{RELATION_PATH}"
    )

    print(
        f"Events output: {EVENT_PATH}"
    )


if __name__ == "__main__":
    main()