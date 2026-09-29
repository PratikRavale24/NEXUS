from backend.app.services.relation_extraction import (
    extract_report_relations,
)


CATALOGS = {
    "PERSON": [
        {
            "person_id": "P001",
            "name": "Rohan Patil",
        },
        {
            "person_id": "P002",
            "name": "Amit Verma",
        },
    ],
    "ORG": [
        {
            "organization_id": "ORG001",
            "name": "Alpha Traders",
        }
    ],
    "LOC": [
        {
            "location_id": "L001",
            "name": "Central Market",
        }
    ],
    "VEHICLE": [],
    "PHONE": [],
}


def person_entity(
    mention: str,
    person_id: str,
    name: str,
    start: int,
    end: int,
):
    return {
        "document_id": "FIR-TEST",
        "case_id": "CASE-001",
        "mention": mention,
        "label": "PERSON",
        "start_char": start,
        "end_char": end,
        "resolution": {
            "person_id": person_id,
            "canonical_name": name,
            "score": 1.0,
            "status": "AUTO_RESOLVED",
        },
    }


def org_entity(
    mention: str,
    start: int,
    end: int,
):
    return {
        "document_id": "FIR-TEST",
        "case_id": "CASE-001",
        "mention": mention,
        "label": "ORG",
        "start_char": start,
        "end_char": end,
    }


def location_entity(
    mention: str,
    start: int,
    end: int,
):
    return {
        "document_id": "FIR-TEST",
        "case_id": "CASE-001",
        "mention": mention,
        "label": "LOC",
        "start_char": start,
        "end_char": end,
    }


def test_meeting_relation():

    text = (
        "Rohan Patil was observed near Central Market "
        "with Amit Verma."
    )

    rohan_start = text.index(
        "Rohan Patil"
    )

    amit_start = text.index(
        "Amit Verma"
    )

    location_start = text.index(
        "Central Market"
    )

    entities = [
        person_entity(
            "Rohan Patil",
            "P001",
            "Rohan Patil",
            rohan_start,
            rohan_start + len(
                "Rohan Patil"
            ),
        ),
        location_entity(
            "Central Market",
            location_start,
            location_start
            + len("Central Market"),
        ),
        person_entity(
            "Amit Verma",
            "P002",
            "Amit Verma",
            amit_start,
            amit_start + len(
                "Amit Verma"
            ),
        ),
    ]

    report = {
        "document_id": "FIR-TEST",
        "case_id": "CASE-001",
        "text": text,
    }

    relationships, events = (
        extract_report_relations(
            report,
            entities,
            CATALOGS,
        )
    )

    relation_types = {
        relationship["relation_type"]
        for relationship in relationships
    }

    assert "MEETS" in relation_types
    assert "SEEN_AT" in relation_types
    assert len(events) == 1


def test_association_relation():

    text = (
        "Rohan Patil was communicating with a "
        "number associated with Alpha Traders."
    )

    rohan_start = text.index(
        "Rohan Patil"
    )

    org_start = text.index(
        "Alpha Traders"
    )

    entities = [
        person_entity(
            "Rohan Patil",
            "P001",
            "Rohan Patil",
            rohan_start,
            rohan_start + len(
                "Rohan Patil"
            ),
        ),
        org_entity(
            "Alpha Traders",
            org_start,
            org_start + len(
                "Alpha Traders"
            ),
        ),
    ]

    report = {
        "document_id": "FIR-TEST",
        "case_id": "CASE-001",
        "text": text,
    }

    relationships, events = (
        extract_report_relations(
            report,
            entities,
            CATALOGS,
        )
    )

    association_relations = [
        relationship
        for relationship in relationships
        if relationship["relation_type"]
        == "ASSOCIATED_WITH"
    ]

    assert len(
        association_relations
    ) == 1

    assert (
        association_relations[0][
            "subject_id"
        ]
        == "P001"
    )

    assert (
        association_relations[0][
            "object_id"
        ]
        == "ORG001"
    )

    assert len(events) == 1