from __future__ import annotations

from neo4j import Driver


def search_entities(
    driver: Driver,
    query: str,
    limit: int = 20,
) -> list[dict]:

    query = query.strip()

    if not query:
        return []

    limit = max(
        1,
        min(limit, 50),
    )

    # Keep each label query isolated.  Apart from being easier to evolve as the
    # graph schema grows, this avoids a Neo4j 5 subquery/UNION planner failure
    # observed with the former single compound query.
    entity_specs = (
        ("Person", "person_id", "name", None),
        ("Phone", "phone_id", "normalized_number", "normalized_number"),
        ("Vehicle", "vehicle_id", "registration", "registration"),
        ("Location", "location_id", "name", None),
        ("Organization", "organization_id", "name", None),
        ("Account", "account_id", "account_number", "account_number"),
    )

    matches: list[dict] = []

    with driver.session() as session:
        for label, id_field, display_field, secondary_field in entity_specs:
            result = session.run(
                f"""
                MATCH (n:{label})
                WHERE toLower(toString(n.{id_field})) CONTAINS toLower($search_term)
                   OR toLower(toString(n.{display_field})) CONTAINS toLower($search_term)
                RETURN n.{id_field} AS entity_id, n.{display_field} AS name
                ORDER BY name
                LIMIT $limit
                """,
                search_term=query,
                limit=limit,
            )
            for record in result:
                data = record.data()
                matches.append(
                    {
                        "entity_id": data["entity_id"],
                        "entity_type": label,
                        "name": data["name"],
                        "secondary_identifier": (
                            data["name"] if secondary_field else None
                        ),
                    }
                )

    return sorted(matches, key=lambda item: (item["entity_type"], item["name"]))[:limit]


def get_entity_profile(
    driver: Driver,
    entity_id: str,
) -> dict | None:

    with driver.session() as session:

        result = session.run(
            """
            CALL () {
                MATCH (p:Person {
                    person_id: $entity_id
                })

                RETURN
                    "Person" AS entity_type,
                    p.person_id AS entity_id,
                    p.name AS name,
                    properties(p) AS properties

                UNION ALL

                MATCH (ph:Phone {
                    phone_id: $entity_id
                })

                RETURN
                    "Phone" AS entity_type,
                    ph.phone_id AS entity_id,
                    ph.normalized_number AS name,
                    properties(ph) AS properties

                UNION ALL

                MATCH (v:Vehicle {
                    vehicle_id: $entity_id
                })

                RETURN
                    "Vehicle" AS entity_type,
                    v.vehicle_id AS entity_id,
                    v.registration AS name,
                    properties(v) AS properties

                UNION ALL

                MATCH (l:Location {
                    location_id: $entity_id
                })

                RETURN
                    "Location" AS entity_type,
                    l.location_id AS entity_id,
                    l.name AS name,
                    properties(l) AS properties

                UNION ALL

                MATCH (o:Organization {
                    organization_id: $entity_id
                })

                RETURN
                    "Organization" AS entity_type,
                    o.organization_id AS entity_id,
                    o.name AS name,
                    properties(o) AS properties

                UNION ALL

                MATCH (a:Account {
                    account_id: $entity_id
                })

                RETURN
                    "Account" AS entity_type,
                    a.account_id AS entity_id,
                    a.account_number AS name,
                    properties(a) AS properties
            }

            RETURN
                entity_type,
                entity_id,
                name,
                properties
            """,
            entity_id=entity_id,
        )

        record = result.single()

        if record is None:
            return None

        data = record.data()

        # Remove internal/technical properties from the
        # primary display object only if necessary.
        properties = data.get(
            "properties"
        ) or {}

        # Count direct relationships.
        connection_result = session.run(
            """
            MATCH (n)
            WHERE
                CASE
                    WHEN $entity_id
                        STARTS WITH "P"
                    THEN n.person_id =
                        $entity_id

                    WHEN $entity_id
                        STARTS WITH "PH"
                    THEN n.phone_id =
                        $entity_id

                    WHEN $entity_id
                        STARTS WITH "V"
                    THEN n.vehicle_id =
                        $entity_id

                    WHEN $entity_id
                        STARTS WITH "L"
                    THEN n.location_id =
                        $entity_id

                    WHEN $entity_id
                        STARTS WITH "ORG"
                    THEN n.organization_id =
                        $entity_id

                    WHEN $entity_id
                        STARTS WITH "ACC"
                    THEN n.account_id =
                        $entity_id

                    ELSE false
                END

            OPTIONAL MATCH (n)--(connected)

            RETURN
                count(DISTINCT connected)
                    AS connection_count
            """,
            entity_id=entity_id,
        )

        connection_record = (
            connection_result.single()
        )

        connection_count = (
            connection_record[
                "connection_count"
            ]
            if connection_record
            else 0
        )

        finding_result = session.run(
            """
            MATCH (f:Finding)
            WHERE
                ($entity_id IN
                    coalesce(f.participants, [])
                )
                OR
                EXISTS {
                    MATCH (n)-[]->(f)
                    WHERE
                        (
                            n.person_id =
                            $entity_id
                        )
                }

            RETURN count(DISTINCT f)
                AS finding_count
            """,
            entity_id=entity_id,
        )

        finding_record = (
            finding_result.single()
        )

        finding_count = (
            finding_record[
                "finding_count"
            ]
            if finding_record
            else 0
        )

        return {
            "entity_id": data[
                "entity_id"
            ],
            "entity_type": data[
                "entity_type"
            ],
            "name": data["name"],
            "properties": properties,
            "connection_count":
                connection_count,
            "finding_count":
                finding_count,
        }
