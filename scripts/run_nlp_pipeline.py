from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from backend.app.services.entity_resolution import (
    resolve_person,
)
from backend.app.services.nlp import extract_entities


ROOT = Path(__file__).resolve().parents[1]

REPORT_PATH = (
    ROOT
    / "data"
    / "raw"
    / "fir"
    / "reports.csv"
)

PERSON_PATH = (
    ROOT
    / "data"
    / "persons.csv"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "processed"
    / "entities"
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "report_entity_mentions.json"
)


def load_person_candidates() -> list[dict]:
    df = pd.read_csv(
        PERSON_PATH
    )

    return df[
        [
            "person_id",
            "name",
        ]
    ].to_dict(
        orient="records"
    )


def main() -> None:

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    reports = pd.read_csv(
        REPORT_PATH
    )

    person_candidates = (
        load_person_candidates()
    )

    output = []

    for _, row in reports.iterrows():

        text = str(row["text"])

        entities = extract_entities(text)

        for entity in entities:

            result = {
                "document_id": row[
                    "document_id"
                ],
                "case_id": row[
                    "case_id"
                ],
                "mention": entity[
                    "mention"
                ],
                "label": entity[
                    "label"
                ],
                "start_char": entity[
                    "start_char"
                ],
                "end_char": entity[
                    "end_char"
                ],
            }

            if entity["label"] == "PERSON":

                resolution = (
                    resolve_person(
                        entity["mention"],
                        person_candidates,
                    )
                )

                result["resolution"] = (
                    resolution
                )

            output.append(result)

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        "NEXUS NLP pipeline completed."
    )

    print(
        f"Extracted {len(output)} entity mentions."
    )

    print(
        f"Output: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()