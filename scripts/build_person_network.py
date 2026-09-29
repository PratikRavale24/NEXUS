from __future__ import annotations

from neo4j import GraphDatabase

from backend.app.config import settings


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

        with driver.session() as session:

            # -----------------------------------------
            # Person-to-person communication network
            # -----------------------------------------

            session.run(
                """
                MATCH
                    (a:Person)-[:OWNS]->(phone_a:Phone)
                    -[call:CALLS]->(phone_b:Phone)
                    <-[:OWNS]-(b:Person)

                WHERE a.person_id <> b.person_id

                WITH
                    a,
                    b,
                    count(call) AS call_count,
                    max(call.timestamp) AS last_seen

                MERGE (a)-[r:COMMUNICATES_WITH]->(b)

                SET
                    r.call_count = call_count,
                    r.last_seen = last_seen,
                    r.network_weight =
                        toFloat(call_count),
                    r.derived_from = "CDR"
                """
            )

            # -----------------------------------------
            # Person-to-person financial network
            # -----------------------------------------

            session.run(
                """
                MATCH
                    (a:Person)-[:OWNS]->(account_a:Account)
                    -[tx:TRANSFERS_TO]->(account_b:Account)
                    <-[:OWNS]-(b:Person)

                WHERE a.person_id <> b.person_id

                WITH
                    a,
                    b,
                    count(tx) AS transaction_count,
                    sum(tx.amount) AS total_amount,
                    max(tx.timestamp) AS last_seen

                MERGE (a)-[r:FINANCIAL_LINK]->(b)

                SET
                    r.transaction_count =
                        transaction_count,
                    r.total_amount =
                        total_amount,
                    r.last_seen =
                        last_seen,
                    r.network_weight =
                        toFloat(transaction_count),
                    r.derived_from = "FINANCIAL"
                """
            )

        print(
            "Person-level investigation network built successfully."
        )

    finally:
        driver.close()


if __name__ == "__main__":
    main()