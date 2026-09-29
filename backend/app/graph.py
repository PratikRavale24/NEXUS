from neo4j import GraphDatabase

from .config import settings


driver = GraphDatabase.driver(
    settings.neo4j_uri,
    auth=(
        settings.neo4j_user,
        settings.neo4j_password,
    ),
)


def check_neo4j() -> bool:
    driver.verify_connectivity()

    with driver.session() as session:
        result = session.run("RETURN 1 AS value")
        record = result.single()

        return record is not None and record["value"] == 1