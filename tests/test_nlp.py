from backend.app.services.nlp import extract_entities


def test_person_extraction():
    text = (
        "Rohan K. Patil was observed near Central Market."
    )

    entities = extract_entities(text)

    person_entities = [
        entity
        for entity in entities
        if entity["label"] == "PERSON"
    ]

    assert any(
        "Rohan K. Patil" in entity["mention"]
        for entity in person_entities
    )


def test_organization_extraction():
    text = (
        "Rohan K. Patil was communicating with "
        "Alpha Traders."
    )

    entities = extract_entities(text)

    org_entities = [
        entity
        for entity in entities
        if entity["label"] == "ORG"
    ]

    assert any(
        entity["mention"] == "Alpha Traders"
        for entity in org_entities
    )


def test_vehicle_extraction():
    text = (
        "Vehicle MH01XX1005 was observed "
        "near Central Market."
    )

    entities = extract_entities(text)

    vehicle_entities = [
        entity
        for entity in entities
        if entity["label"] == "VEHICLE"
    ]

    assert any(
        entity["mention"] == "MH01XX1005"
        for entity in vehicle_entities
    )


def test_phone_extraction():
    text = (
        "Contact number 9876543210 was "
        "associated with the report."
    )

    entities = extract_entities(text)

    phone_entities = [
        entity
        for entity in entities
        if entity["label"] == "PHONE"
    ]

    assert any(
        entity["mention"] == "9876543210"
        for entity in phone_entities
    )