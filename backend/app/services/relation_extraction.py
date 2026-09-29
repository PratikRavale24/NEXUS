from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import pandas as pd

from .nlp import get_nlp


PROJECT_ROOT = Path(__file__).resolve().parents[3]


ENTITY_TYPE_MAP = {
    "PERSON": {
        "neo4j_label": "Person",
        "id_field": "person_id",
        "name_field": "name",
    },
    "ORG": {
        "neo4j_label": "Organization",
        "id_field": "organization_id",
        "name_field": "name",
    },
    "LOC": {
        "neo4j_label": "Location",
        "id_field": "location_id",
        "name_field": "name",
    },
    "VEHICLE": {
        "neo4j_label": "Vehicle",
        "id_field": "vehicle_id",
        "name_field": "registration",
    },
    "PHONE": {
        "neo4j_label": "Phone",
        "id_field": "phone_id",
        "name_field": "phone_number",
    },
}


MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


DATE_PATTERN = re.compile(
    r"\b(\d{1,2})\s+"
    r"(January|February|March|April|May|June|July|August|"
    r"September|October|November|December)"
    r"\s+(\d{4})\b",
    re.IGNORECASE,
)


def normalize(value: str) -> str:
    """
    Normalize text for catalog matching.
    """

    value = str(value).lower().strip()

    value = re.sub(
        r"[^\w\s]",
        " ",
        value,
    )

    value = re.sub(
        r"\s+",
        " ",
        value,
    )

    return value.strip()


def normalize_phone(value: str) -> str:
    """
    Keep only digits for phone comparison.
    """

    return re.sub(
        r"\D",
        "",
        str(value),
    )


def load_catalogs() -> dict[str, list[dict]]:
    """
    Load canonical entity catalogs generated
    by the synthetic-data generator.
    """

    data_dir = PROJECT_ROOT / "data"

    catalogs = {
        "ORG": pd.read_csv(
            data_dir / "organizations.csv"
        ).to_dict("records"),

        "LOC": pd.read_csv(
            data_dir / "locations.csv"
        ).to_dict("records"),

        "VEHICLE": pd.read_csv(
            data_dir / "vehicles.csv"
        ).to_dict("records"),

        "PHONE": pd.read_csv(
            data_dir / "phones.csv"
        ).to_dict("records"),

        "PERSON": pd.read_csv(
            data_dir / "persons.csv"
        ).to_dict("records"),
    }

    return catalogs


def resolve_entity(
    entity: dict,
    catalogs: dict[str, list[dict]],
) -> dict | None:
    """
    Resolve an extracted mention to a canonical entity.
    """

    label = entity["label"]

    if label not in ENTITY_TYPE_MAP:
        return None

    # PERSON already has the entity-resolution result
    # produced by our previous pipeline.
    if label == "PERSON":

        resolution = entity.get(
            "resolution"
        )

        if not resolution:
            return None

        person_id = resolution.get(
            "person_id"
        )

        canonical_name = resolution.get(
            "canonical_name"
        )

        if not person_id:
            return None

        return {
            "entity_type": "Person",
            "entity_id": person_id,
            "canonical_name": canonical_name,
            "mention": entity["mention"],
            "label": label,
        }

    candidates = catalogs[label]

    mention_normalized = normalize(
        entity["mention"]
    )

    for candidate in candidates:

        if label == "PHONE":

            candidate_value = normalize_phone(
                candidate["phone_number"]
            )

            if (
                normalize_phone(
                    entity["mention"]
                )
                == candidate_value
            ):
                return {
                    "entity_type": "Phone",
                    "entity_id": candidate[
                        "phone_id"
                    ],
                    "canonical_name": candidate[
                        "phone_number"
                    ],
                    "mention": entity[
                        "mention"
                    ],
                    "label": label,
                }

        else:

            map_info = ENTITY_TYPE_MAP[label]

            candidate_value = normalize(
                candidate[
                    map_info["name_field"]
                ]
            )

            if (
                mention_normalized
                == candidate_value
            ):
                return {
                    "entity_type": map_info[
                        "neo4j_label"
                    ],
                    "entity_id": candidate[
                        map_info["id_field"]
                    ],
                    "canonical_name": candidate[
                        map_info["name_field"]
                    ],
                    "mention": entity[
                        "mention"
                    ],
                    "label": label,
                }

    return None


def parse_report_date(
    text: str,
) -> dict | None:
    """
    Extract a report date.

    Current synthetic data uses dates such as:
    12 August 2026
    """

    match = DATE_PATTERN.search(text)

    if not match:
        return None

    day = int(match.group(1))
    month = MONTHS[
        match.group(2).lower()
    ]
    year = int(match.group(3))

    date_value = datetime(
        year,
        month,
        day,
    )

    return {
        "timestamp": date_value.isoformat(),
        "time_precision": "day",
    }


def create_relationship(
    subject: dict,
    relation_type: str,
    object_entity: dict,
    evidence_id: str,
    case_id: str,
    confidence: float,
    sentence: str,
) -> dict:

    return {
        "subject_type": subject[
            "entity_type"
        ],
        "subject_id": subject[
            "entity_id"
        ],
        "subject_name": subject[
            "canonical_name"
        ],
        "relation_type": relation_type,
        "object_type": object_entity[
            "entity_type"
        ],
        "object_id": object_entity[
            "entity_id"
        ],
        "object_name": object_entity[
            "canonical_name"
        ],
        "evidence_id": evidence_id,
        "case_id": case_id,
        "confidence": confidence,
        "extraction_method": "rule_based",
        "source_sentence": sentence,
    }


def contains_any(
    text: str,
    phrases: list[str],
) -> bool:

    return any(
        phrase in text
        for phrase in phrases
    )


def extract_sentence_relations(
    sentence: str,
    resolved_entities: list[tuple[dict, dict]],
    evidence_id: str,
    case_id: str,
) -> list[dict]:
    """
    Extract relations from one sentence.

    resolved_entities contains:
        (original_entity, canonical_entity)
    """

    relations = []

    lower_sentence = sentence.lower()

    persons = [
        canonical
        for _, canonical in resolved_entities
        if canonical["entity_type"] == "Person"
    ]

    organizations = [
        canonical
        for _, canonical in resolved_entities
        if canonical["entity_type"]
        == "Organization"
    ]

    locations = [
        canonical
        for _, canonical in resolved_entities
        if canonical["entity_type"]
        == "Location"
    ]

    vehicles = [
        canonical
        for _, canonical in resolved_entities
        if canonical["entity_type"]
        == "Vehicle"
    ]

    # --------------------------------------------------
    # PERSON -> ORGANIZATION
    # ASSOCIATED_WITH
    # --------------------------------------------------

    if persons and organizations:

        if contains_any(
            lower_sentence,
            [
                "associated with",
                "associated to",
                "linked with",
                "connected with",
            ],
        ):

            for person in persons:
                for organization in organizations:

                    relations.append(
                        create_relationship(
                            person,
                            "ASSOCIATED_WITH",
                            organization,
                            evidence_id,
                            case_id,
                            0.92,
                            sentence,
                        )
                    )

    # --------------------------------------------------
    # PERSON -> LOCATION
    # SEEN_AT
    # --------------------------------------------------

    if persons and locations:

        observation_sentence = contains_any(
            lower_sentence,
            [
                "observed",
                "seen",
                "spotted",
                "reported near",
            ],
        )

        location_context = contains_any(
            lower_sentence,
            [
                "near",
                "at",
                "inside",
                "outside",
            ],
        )

        if (
            observation_sentence
            and location_context
        ):

            for person in persons:
                for location in locations:

                    relations.append(
                        create_relationship(
                            person,
                            "SEEN_AT",
                            location,
                            evidence_id,
                            case_id,
                            0.90,
                            sentence,
                        )
                    )

    # --------------------------------------------------
    # PERSON -> PERSON
    # MEETS
    # --------------------------------------------------

    if len(persons) >= 2:

        meeting_context = contains_any(
            lower_sentence,
            [
                "with",
                "meeting",
                "met",
            ],
        )

        observation_context = contains_any(
            lower_sentence,
            [
                "observed",
                "seen",
                "spotted",
            ],
        )

        if (
            meeting_context
            or (
                observation_context
                and " and " in lower_sentence
            )
        ):

            for index in range(
                len(persons)
            ):

                for jndex in range(
                    index + 1,
                    len(persons),
                ):

                    relations.append(
                        create_relationship(
                            persons[index],
                            "MEETS",
                            persons[jndex],
                            evidence_id,
                            case_id,
                            0.86,
                            sentence,
                        )
                    )

    # --------------------------------------------------
    # PERSON -> VEHICLE
    # USES
    #
    # Only infer this when the text actually indicates
    # vehicle use rather than merely co-location.
    # --------------------------------------------------

    if persons and vehicles:

        usage_context = contains_any(
            lower_sentence,
            [
                "used",
                "using",
                "driving",
                "operated",
            ],
        )

        if usage_context:

            for person in persons:
                for vehicle in vehicles:

                    relations.append(
                        create_relationship(
                            person,
                            "USES",
                            vehicle,
                            evidence_id,
                            case_id,
                            0.88,
                            sentence,
                        )
                    )

    return relations


def extract_report_relations(
    report: dict,
    entities: list[dict],
    catalogs: dict[str, list[dict]],
) -> tuple[list[dict], list[dict]]:

    text = str(report["text"])

    evidence_id = report[
        "document_id"
    ]

    case_id = report[
        "case_id"
    ]

    nlp = get_nlp()

    doc = nlp(text)

    report_date = parse_report_date(
        text
    )

    relationships = []

    events = []

    for sentence_index, sent in enumerate(
        doc.sents,
        start=1,
    ):

        sentence_text = sent.text.strip()

        if not sentence_text:
            continue

        sentence_start = (
            sent.start_char
        )

        sentence_end = (
            sent.end_char
        )

        sentence_entities = [
            entity
            for entity in entities
            if entity["start_char"]
            >= sentence_start
            and entity["end_char"]
            <= sentence_end
        ]

        resolved_entities = []

        for entity in sentence_entities:

            canonical = resolve_entity(
                entity,
                catalogs,
            )

            if canonical:
                resolved_entities.append(
                    (
                        entity,
                        canonical,
                    )
                )

        if not resolved_entities:
            continue

        # Evidence linkage for every canonical entity.
        for _, canonical in resolved_entities:

            relationships.append(
                {
                    "subject_type": canonical[
                        "entity_type"
                    ],
                    "subject_id": canonical[
                        "entity_id"
                    ],
                    "subject_name": canonical[
                        "canonical_name"
                    ],
                    "relation_type": "MENTIONED_IN",
                    "object_type": "Evidence",
                    "object_id": evidence_id,
                    "object_name": evidence_id,
                    "evidence_id": evidence_id,
                    "case_id": case_id,
                    "confidence": 1.0,
                    "extraction_method": "entity_linking",
                    "source_sentence": sentence_text,
                }
            )

        extracted = extract_sentence_relations(
            sentence_text,
            resolved_entities,
            evidence_id,
            case_id,
        )

        relationships.extend(
            extracted
        )

        semantic_relations = [
            r
            for r in extracted
            if r["relation_type"]
            != "MENTIONED_IN"
        ]

        if semantic_relations:

            relation_types = {
                relation[
                    "relation_type"
                ]
                for relation
                in semantic_relations
            }

            if "MEETS" in relation_types:
                event_type = "MEETING"

            elif "SEEN_AT" in relation_types:
                event_type = "OBSERVATION"

            elif (
                "ASSOCIATED_WITH"
                in relation_types
            ):
                event_type = "ASSOCIATION"

            elif "USES" in relation_types:
                event_type = "VEHICLE_USAGE"

            else:
                event_type = "OTHER"

            event_id = (
                f"EVT-{evidence_id}-"
                f"{sentence_index:02d}"
            )

            events.append(
                {
                    "event_id": event_id,
                    "event_type": event_type,
                    "case_id": case_id,
                    "evidence_id": evidence_id,
                    "timestamp": (
                        report_date[
                            "timestamp"
                        ]
                        if report_date
                        else None
                    ),
                    "time_precision": (
                        report_date[
                            "time_precision"
                        ]
                        if report_date
                        else None
                    ),
                    "description": sentence_text,
                    "entity_ids": [
                        {
                            "entity_type": canonical[
                                "entity_type"
                            ],
                            "entity_id": canonical[
                                "entity_id"
                            ],
                            "name": canonical[
                                "canonical_name"
                            ],
                        }
                        for _, canonical
                        in resolved_entities
                    ],
                    "relation_types": sorted(
                        relation_types
                    ),
                }
            )

    return relationships, events