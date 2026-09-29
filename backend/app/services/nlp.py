from __future__ import annotations

import re
from functools import lru_cache

import spacy


# --------------------------------------------------
# Domain-specific entity dictionaries
# --------------------------------------------------

DOMAIN_ORGANIZATIONS = {
    "alpha traders",
    "vertex logistics",
    "metro supplies",
    "orion exports",
    "prime services",
}

DOMAIN_LOCATIONS = {
    "central market",
    "north railway station",
    "riverside warehouse",
    "city bus depot",
    "east industrial area",
    "central mall",
    "harbor road",
    "old highway junction",
    "west logistics hub",
    "metro parking area",
}


# --------------------------------------------------
# spaCy model
# --------------------------------------------------

@lru_cache(maxsize=1)
def get_nlp():
    """
    Load the spaCy model once and reuse it.
    """

    return spacy.load("en_core_web_sm")


# --------------------------------------------------
# Deterministic identifier patterns
# --------------------------------------------------

PHONE_PATTERN = re.compile(
    r"(?<!\d)(?:\+?91[-\s]?)?\d{10,12}(?!\d)"
)

VEHICLE_PATTERN = re.compile(
    r"\b[A-Z]{2}\d{2}[A-Z]{1,3}\d{4}\b"
)

INITIAL_NAME_PATTERN = re.compile(
    r"\b[A-Z]\.\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b"
)


# --------------------------------------------------
# Utilities
# --------------------------------------------------

def normalize_for_lookup(value: str) -> str:
    """
    Normalize text for exact domain matching.
    """

    value = value.lower().strip()

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


# --------------------------------------------------
# spaCy extraction
# --------------------------------------------------

def extract_ner_entities(text: str) -> list[dict]:
    """
    Extract named entities using spaCy's general NER model.
    """

    nlp = get_nlp()

    doc = nlp(text)

    entities = []

    for ent in doc.ents:
        entities.append(
            {
                "mention": ent.text,
                "label": ent.label_,
                "start_char": ent.start_char,
                "end_char": ent.end_char,
                "source": "spacy",
            }
        )

    return entities


# --------------------------------------------------
# Domain-specific corrections
# --------------------------------------------------

def apply_domain_overrides(
    text: str,
    entities: list[dict],
) -> list[dict]:
    """
    Apply NEXUS domain knowledge after generic NER.

    This allows known organizations and locations to
    override an incorrect generic NER classification.
    """

    corrected = entities.copy()

    override_groups = [
        (DOMAIN_ORGANIZATIONS, "ORG"),
        (DOMAIN_LOCATIONS, "LOC"),
    ]

    for vocabulary, label in override_groups:

        for phrase in vocabulary:

            pattern = re.compile(
                re.escape(phrase),
                flags=re.IGNORECASE,
            )

            for match in pattern.finditer(text):

                start = match.start()
                end = match.end()

                # Remove overlapping entities generated
                # by generic NER.
                corrected = [
                    entity
                    for entity in corrected
                    if (
                        entity["end_char"] <= start
                        or entity["start_char"] >= end
                    )
                ]

                corrected.append(
                    {
                        "mention": match.group(),
                        "label": label,
                        "start_char": start,
                        "end_char": end,
                        "source": "domain_rule",
                    }
                )

    return corrected


# --------------------------------------------------
# Structured identifiers
# --------------------------------------------------

def extract_structured_identifiers(
    text: str,
) -> list[dict]:
    """
    Extract highly structured entities using deterministic
    patterns.
    """

    entities = []

    # Phone numbers
    for match in PHONE_PATTERN.finditer(text):

        entities.append(
            {
                "mention": match.group(),
                "label": "PHONE",
                "start_char": match.start(),
                "end_char": match.end(),
                "source": "rule",
            }
        )

    # Vehicle registration
    for match in VEHICLE_PATTERN.finditer(text):

        entities.append(
            {
                "mention": match.group(),
                "label": "VEHICLE",
                "start_char": match.start(),
                "end_char": match.end(),
                "source": "rule",
            }
        )

    # Initial-based person names
    for match in INITIAL_NAME_PATTERN.finditer(text):

        entities.append(
            {
                "mention": match.group(),
                "label": "PERSON",
                "start_char": match.start(),
                "end_char": match.end(),
                "source": "rule",
            }
        )

    return entities


# --------------------------------------------------
# Complete NEXUS entity extraction
# --------------------------------------------------

def extract_entities(
    text: str,
) -> list[dict]:
    """
    NEXUS hybrid entity extraction pipeline.

    1. Generic spaCy NER
    2. Domain-specific correction
    3. Deterministic identifier extraction
    4. Duplicate/overlap removal
    """

    entities = extract_ner_entities(text)

    # Correct general-model mistakes.
    entities = apply_domain_overrides(
        text,
        entities,
    )

    # Add highly structured identifiers.
    entities.extend(
        extract_structured_identifiers(text)
    )

    # Remove exact duplicate spans.
    unique = {}

    for entity in entities:

        key = (
            entity["start_char"],
            entity["end_char"],
        )

        unique[key] = entity

    # Sort by position in document.
    return sorted(
        unique.values(),
        key=lambda item: item["start_char"],
    )