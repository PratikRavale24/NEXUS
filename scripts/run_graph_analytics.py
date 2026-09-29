from __future__ import annotations

from neo4j import GraphDatabase

from backend.app.config import settings


GRAPH_NAME = "nexusPersonNetwork"


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

            # ------------------------------------------------
            # Remove an existing in-memory projection.
            # This does NOT delete stored Neo4j data.
            # ------------------------------------------------

            session.run(
                """
                CALL gds.graph.drop(
                    $graph_name,
                    false
                )
                YIELD graphName
                RETURN graphName
                """,
                graph_name=GRAPH_NAME,
            )

            # ------------------------------------------------
            # Create the unified person investigation graph.
            # We intentionally use an unweighted projection
            # because the three relationship types do not
            # share a common comparable weight property.
            # ------------------------------------------------

            result = session.run(
                """
                CALL gds.graph.project(
                    $graph_name,
                    'Person',
                    {
                        COMMUNICATES_WITH: {
                            orientation: 'UNDIRECTED'
                        },
                        MEETS: {
                            orientation: 'UNDIRECTED'
                        },
                        FINANCIAL_LINK: {
                            orientation: 'UNDIRECTED'
                        }
                    }
                )
                YIELD
                    graphName,
                    nodeCount,
                    relationshipCount
                RETURN
                    graphName,
                    nodeCount,
                    relationshipCount
                """,
                graph_name=GRAPH_NAME,
            )

            projection = result.single()

            print(
                f"Projected graph: {projection['graphName']}"
            )

            print(
                f"Nodes: {projection['nodeCount']}"
            )

            print(
                f"Relationships: "
                f"{projection['relationshipCount']}"
            )

            # ------------------------------------------------
            # Degree Centrality
            # ------------------------------------------------

            result = session.run(
                """
                CALL gds.degree.write(
                    $graph_name,
                    {
                        writeProperty: 'nexus_degree',
                        orientation: 'UNDIRECTED'
                    }
                )
                YIELD nodePropertiesWritten
                RETURN nodePropertiesWritten
                """,
                graph_name=GRAPH_NAME,
            )

            print(
                "Degree:",
                result.single()[
                    "nodePropertiesWritten"
                ],
            )

            # ------------------------------------------------
            # Betweenness Centrality
            # ------------------------------------------------

            result = session.run(
                """
                CALL gds.betweenness.write(
                    $graph_name,
                    {
                        writeProperty:
                            'nexus_betweenness'
                    }
                )
                YIELD nodePropertiesWritten
                RETURN nodePropertiesWritten
                """,
                graph_name=GRAPH_NAME,
            )

            print(
                "Betweenness:",
                result.single()[
                    "nodePropertiesWritten"
                ],
            )

            # ------------------------------------------------
            # PageRank
            # Unweighted for the unified graph.
            # ------------------------------------------------

            result = session.run(
                """
                CALL gds.pageRank.write(
                    $graph_name,
                    {
                        writeProperty:
                            'nexus_pagerank'
                    }
                )
                YIELD nodePropertiesWritten
                RETURN nodePropertiesWritten
                """,
                graph_name=GRAPH_NAME,
            )

            print(
                "PageRank:",
                result.single()[
                    "nodePropertiesWritten"
                ],
            )

            # ------------------------------------------------
            # Louvain
            # Unweighted unified network.
            # ------------------------------------------------

            result = session.run(
                """
                CALL gds.louvain.write(
                    $graph_name,
                    {
                        writeProperty:
                            'nexus_community'
                    }
                )
                YIELD
                    communityCount,
                    modularity,
                    nodePropertiesWritten
                RETURN
                    communityCount,
                    modularity,
                    nodePropertiesWritten
                """,
                graph_name=GRAPH_NAME,
            )

            louvain = result.single()

            print(
                "Louvain communities:",
                louvain["communityCount"],
            )

            print(
                "Louvain modularity:",
                louvain["modularity"],
            )

            print(
                "Community properties written:",
                louvain[
                    "nodePropertiesWritten"
                ],
            )

            print(
                "NEXUS graph analytics completed."
            )

    finally:
        driver.close()


if __name__ == "__main__":
    main()