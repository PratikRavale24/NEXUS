from __future__ import annotations

from neo4j import Driver


def get_person_timeline(
    driver: Driver,
    person_id: str,
    limit: int = 200,
) -> list[dict]:

    limit = max(
        1,
        min(limit, 500),
    )

    with driver.session() as session:

        result = session.run(
            """
            CALL () {
                // --------------------------------------
                // Explicit Event nodes
                // --------------------------------------

                MATCH
                    (p:Person {
                        person_id: $person_id
                    })
                    -[:INVOLVED_IN]->
                    (e:Event)

                RETURN
                    e.timestamp AS timestamp,
                    e.event_type AS event_type,
                    e.description AS description,
                    p.person_id AS entity_id,
                    p.name AS entity_name,
                    NULL AS related_entity_id,
                    NULL AS related_entity_name,
                    e.case_id AS case_id,
                    e.evidence_id AS evidence_id,
                    "EVENT" AS source_type

                UNION ALL

                // --------------------------------------
                // CDR activity
                // --------------------------------------

                MATCH
                    (p:Person {
                        person_id: $person_id
                    })
                    -[:OWNS]->
                    (ph:Phone)
                    -[c:CALLS]->
                    (other_phone:Phone)

                RETURN
                    c.timestamp AS timestamp,
                    "CALL" AS event_type,
                    "Outgoing call" AS description,
                    p.person_id AS entity_id,
                    p.name AS entity_name,
                    other_phone.phone_id
                        AS related_entity_id,
                    other_phone.normalized_number
                        AS related_entity_name,
                    c.case_id AS case_id,
                    c.evidence_id AS evidence_id,
                    "CDR" AS source_type

                UNION ALL

                // --------------------------------------
                // Surveillance: seen at location
                // --------------------------------------

                MATCH
                    (p:Person {
                        person_id: $person_id
                    })
                    -[r:SEEN_AT]->
                    (l:Location)

                RETURN
                    r.timestamp AS timestamp,
                    "SEEN_AT" AS event_type,
                    "Observed at location"
                        AS description,
                    p.person_id AS entity_id,
                    p.name AS entity_name,
                    l.location_id
                        AS related_entity_id,
                    l.name
                        AS related_entity_name,
                    r.case_id AS case_id,
                    r.evidence_id
                        AS evidence_id,
                    "SURVEILLANCE"
                        AS source_type

                UNION ALL

                // --------------------------------------
                // Surveillance: vehicle usage
                // --------------------------------------

                MATCH
                    (p:Person {
                        person_id: $person_id
                    })
                    -[r:USES]->
                    (v:Vehicle)

                RETURN
                    r.timestamp AS timestamp,
                    "USES_VEHICLE" AS event_type,
                    "Vehicle observed in use"
                        AS description,
                    p.person_id AS entity_id,
                    p.name AS entity_name,
                    v.vehicle_id
                        AS related_entity_id,
                    v.registration
                        AS related_entity_name,
                    r.case_id AS case_id,
                    r.evidence_id
                        AS evidence_id,
                    "SURVEILLANCE"
                        AS source_type

                UNION ALL

                // --------------------------------------
                // Financial activity
                // --------------------------------------

                MATCH
                    (p:Person {
                        person_id: $person_id
                    })
                    -[:OWNS]->
                    (a:Account)
                    -[t:TRANSFERS_TO]->
                    (target:Account)

                RETURN
                    t.timestamp AS timestamp,
                    "FINANCIAL_TRANSFER"
                        AS event_type,
                    "Financial transfer"
                        AS description,
                    p.person_id AS entity_id,
                    p.name AS entity_name,
                    target.account_id
                        AS related_entity_id,
                    target.account_number
                        AS related_entity_name,
                    t.case_id AS case_id,
                    t.evidence_id
                        AS evidence_id,
                    "FINANCIAL"
                        AS source_type
            }

            RETURN
                timestamp,
                event_type,
                description,
                entity_id,
                entity_name,
                related_entity_id,
                related_entity_name,
                case_id,
                evidence_id,
                source_type

            ORDER BY
                timestamp DESC

            LIMIT $limit
            """,
            person_id=person_id,
            limit=limit,
        )

        timeline = []

        for record in result:

            data = record.data()

            timestamp = data.get(
                "timestamp"
            )

            if hasattr(
                timestamp,
                "to_native",
            ):
                timestamp = (
                    timestamp.to_native()
                )

            data["timestamp"] = timestamp

            timeline.append(data)

        return timeline