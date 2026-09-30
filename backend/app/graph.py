from collections.abc import Iterator
from contextlib import contextmanager

from neo4j import Driver, GraphDatabase

from .config import settings


driver = GraphDatabase.driver(
    settings.neo4j_uri,
    auth=(
        settings.neo4j_user,
        settings.neo4j_password,
    ),
)


@contextmanager
def session() -> Iterator:
    """Yield a short-lived session from the application-scoped driver."""
    with driver.session() as graph_session:
        yield graph_session


def close_driver() -> None:
    driver.close()


def check_neo4j() -> bool:
    driver.verify_connectivity()

    with driver.session() as session:
        result = session.run("RETURN 1 AS value")
        record = result.single()

        return record is not None and record["value"] == 1