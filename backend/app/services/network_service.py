from __future__ import annotations

from neo4j import Driver


def _json_safe(value):
    """Convert Neo4j temporal values nested in relationship properties."""
    if hasattr(value, "to_native"):
        return value.to_native()
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _node_id(
    node: dict,
) -> tuple[str, str]:

    if node.get("person_id") is not None:
        return (
            "Person",
            node["person_id"],
        )

    if node.get("phone_id") is not None:
        return (
            "Phone",
            node["phone_id"],
        )

    if node.get("vehicle_id") is not None:
        return (
            "Vehicle",
            node["vehicle_id"],
        )

    if node.get("location_id") is not None:
        return (
            "Location",
            node["location_id"],
        )

    if node.get("organization_id") is not None:
        return (
            "Organization",
            node["organization_id"],
        )

    if node.get("account_id") is not None:
        return (
            "Account",
            node["account_id"],
        )

    if node.get("event_id") is not None:
        return (
            "Event",
            node["event_id"],
        )

    if node.get("evidence_id") is not None:
        return (
            "Evidence",
            node["evidence_id"],
        )

    if node.get("finding_id") is not None:
        return (
            "Finding",
            node["finding_id"],
        )

    return (
        "Unknown",
        str(node.element_id),
    )


def _node_label(
    entity_type: str,
    node: dict,
) -> str:

    if entity_type == "Person":
        return node.get(
            "name",
            node.get("person_id", "Person"),
        )

    if entity_type == "Phone":
        return node.get(
            "normalized_number",
            node.get("phone_id", "Phone"),
        )

    if entity_type == "Vehicle":
        return node.get(
            "registration",
            node.get("vehicle_id", "Vehicle"),
        )

    if entity_type == "Location":
        return node.get(
            "name",
            node.get("location_id", "Location"),
        )

    if entity_type == "Organization":
        return node.get(
            "name",
            node.get(
                "organization_id",
                "Organization",
            ),
        )

    if entity_type == "Account":
        return node.get(
            "account_number",
            node.get("account_id", "Account"),
        )

    if entity_type == "Event":
        return node.get(
            "description",
            node.get("event_id", "Event"),
        )

    if entity_type == "Evidence":
        return node.get(
            "evidence_id",
            "Evidence",
        )

    if entity_type == "Finding":
        return node.get(
            "finding_id",
            "Finding",
        )

    return str(node.element_id)


def get_person_network(
    driver: Driver,
    person_id: str,
    depth: int = 1,
    node_limit: int = 250,
    edge_limit: int = 500,
) -> dict | None:

    depth = max(
        1,
        min(depth, 2),
    )
    node_limit = max(1, min(node_limit, 500))
    edge_limit = max(1, min(edge_limit, 1000))

    with driver.session() as session:

        # Confirm root exists.
        root_result = session.run(
            """
            MATCH (p:Person {
                person_id: $person_id
            })
            RETURN p
            """,
            person_id=person_id,
        )

        root_record = (
            root_result.single()
        )

        if root_record is None:
            return None

        root_node = root_record["p"]

        nodes: dict[str, dict] = {}
        edges: dict[str, dict] = {}

        root_type, root_id = _node_id(
            dict(root_node)
        )

        root_properties = dict(
            root_node
        )

        nodes[root_id] = {
            "id": root_id,
            "entity_type": root_type,
            "label": _node_label(
                root_type,
                root_properties,
            ),
            "properties": _json_safe(root_properties),
        }

        result = session.run(
            f"""
            MATCH path =
                (root:Person {{
                    person_id: $person_id
                }})
                -[*1..{depth}]-
                (connected)

            UNWIND
                nodes(path) AS path_node

            WITH
                path,
                path_node

            RETURN
                path,
                path_node
                LIMIT $path_limit
            """,
            person_id=person_id,
            path_limit=edge_limit,
        )

        for record in result:

            path = record["path"]
            path_node = record[
                "path_node"
            ]

            node_properties = dict(
                path_node
            )

            entity_type, entity_id = _node_id(
                node_properties
            )

            if entity_id not in nodes:

                nodes[entity_id] = {
                    "id": entity_id,
                    "entity_type":
                        entity_type,
                    "label":
                        _node_label(
                            entity_type,
                            node_properties,
                        ),
                    "properties": _json_safe(node_properties),
                }

            for relationship in (
                path.relationships
            ):

                source_node = (
                    relationship.nodes[0]
                )

                target_node = (
                    relationship.nodes[-1]
                )

                source_type, source_id = (
                    _node_id(
                        dict(source_node)
                    )
                )

                target_type, target_id = (
                    _node_id(
                        dict(target_node)
                    )
                )

                edge_key = (
                    f"{source_id}|"
                    f"{relationship.type}|"
                    f"{target_id}|"
                    f"{relationship.element_id}"
                )

                if edge_key in edges:
                    continue

                edges[edge_key] = {
                    "id": edge_key,
                    "source": source_id,
                    "target": target_id,
                    "relationship":
                        relationship.type,
                    "properties": _json_safe(dict(relationship)),
                }

                if len(edges) >= edge_limit:
                    break

            if len(nodes) >= node_limit and len(edges) >= edge_limit:
                break

        return {
            "root_entity_id": person_id,
            "depth": depth,
            "nodes": list(nodes.values())[:node_limit],
            "edges": list(edges.values())[:edge_limit],
        }
