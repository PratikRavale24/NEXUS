from backend.app.services.entity_resolution import (
    resolve_person,
)


PERSONS = [
    {
        "person_id": "P001",
        "name": "Rohan Patil",
    },
    {
        "person_id": "P002",
        "name": "Amit Verma",
    },
    {
        "person_id": "P003",
        "name": "Karan Shah",
    },
]


def test_exact_person_match():
    result = resolve_person(
        "Rohan Patil",
        PERSONS,
    )

    assert result["person_id"] == "P001"
    assert result["score"] == 1.0


def test_middle_name_variant():
    result = resolve_person(
        "Rohan K. Patil",
        PERSONS,
    )

    assert result["person_id"] == "P001"
    assert result["score"] >= 0.90


def test_initial_variant():
    result = resolve_person(
        "R. Patil",
        PERSONS,
    )

    assert result["person_id"] == "P001"
    assert result["score"] >= 0.90