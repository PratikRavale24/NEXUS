from backend.app.config import settings
from backend.app.services.ingestion import run_ingestion
from neo4j import GraphDatabase


def main() -> None:
    driver = GraphDatabase.driver(
        settings.neo4j_uri,
        auth=(
            settings.neo4j_user,
            settings.neo4j_password,
        ),
    )

    try:
        driver.verify_connectivity()

        print("Connected to Neo4j.")
        print("Starting NEXUS data ingestion...")

        run_ingestion(driver)

        print("NEXUS data ingestion completed successfully.")

    finally:
        driver.close()


if __name__ == "__main__":
    main()
    