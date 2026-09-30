from datetime import datetime

from backend.app.schemas.entity import (
    EntityProfile,
    EntitySearchResult,
    NetworkResponse,
    TimelineResponse,
)


def test_entity_search_schema():

    result = EntitySearchResult(
        entity_id="P001",
        entity_type="Person",
        name="Rohan Patil",
    )

    assert result.entity_id == "P001"
    assert result.entity_type == "Person"


def test_entity_profile_schema():

    profile = EntityProfile(
        entity_id="P001",
        entity_type="Person",
        name="Rohan Patil",
        properties={
            "person_id": "P001"
        },
        connection_count=3,
        finding_count=1,
    )

    assert profile.connection_count == 3
    assert profile.finding_count == 1


def test_network_schema():

    response = NetworkResponse(
        root_entity_id="P001",
        depth=1,
        nodes=[],
        edges=[],
    )

    assert response.root_entity_id == "P001"
    assert response.depth == 1


def test_timeline_schema():

    response = TimelineResponse(
        entity_id="P001",
        items=[
            {
                "timestamp":
                    datetime(
                        2026,
                        8,
                        18,
                        21,
                        0,
                    ),
                "event_type": "SEEN_AT",
                "description":
                    "Observed at location",
            }
        ],
    )

    assert len(response.items) == 1