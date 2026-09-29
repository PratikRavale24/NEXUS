from __future__ import annotations

from pathlib import Path

import pandas as pd

from backend.app.config import settings
from neo4j import GraphDatabase


ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
OUTPUT_DIR = DATA_DIR / "processed" / "anomalies"
OUTPUT_PATH = OUTPUT_DIR / "person_anomaly_features.csv"


def load_graph_features() -> pd.DataFrame:
    """
    Read the network-analysis properties that were
    previously written onto Person nodes.
    """

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
            result = session.run(
                """
                MATCH (p:Person)
                RETURN
                    p.person_id AS person_id,
                    p.name AS person_name,
                    coalesce(p.nexus_degree, 0)
                        AS degree,
                    coalesce(
                        p.nexus_betweenness,
                        0
                    ) AS betweenness,
                    coalesce(
                        p.nexus_pagerank,
                        0
                    ) AS pagerank
                ORDER BY p.person_id
                """
            )

            rows = [
                record.data()
                for record in result
            ]

        return pd.DataFrame(rows)

    finally:
        driver.close()


def main() -> None:

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------
    # Load source data
    # --------------------------------------------------

    persons = pd.read_csv(
        DATA_DIR / "persons.csv"
    )

    phone_ownership = pd.read_csv(
        DATA_DIR / "phone_ownership.csv"
    )

    account_ownership = pd.read_csv(
        DATA_DIR / "account_ownership.csv"
    )

    accounts = pd.read_csv(
        DATA_DIR / "accounts.csv"
    )

    phones = pd.read_csv(
        DATA_DIR / "phones.csv"
    )

    cdr = pd.read_csv(
        DATA_DIR / "raw" / "cdr" / "cdr.csv"
    )

    financial = pd.read_csv(
        DATA_DIR
        / "raw"
        / "financial"
        / "transactions.csv"
    )

    surveillance = pd.read_csv(
        DATA_DIR
        / "raw"
        / "surveillance"
        / "surveillance.csv"
    )

    # --------------------------------------------------
    # Phone ownership
    # --------------------------------------------------

    phone_to_person = dict(
        zip(
            phone_ownership["phone_id"],
            phone_ownership["person_id"],
        )
    )

    cdr["caller_person_id"] = (
        cdr["from_phone"].map(
            phone_to_person
        )
    )

    cdr["receiver_person_id"] = (
        cdr["to_phone"].map(
            phone_to_person
        )
    )

    # Remove calls where the owner cannot be mapped.
    cdr = cdr.dropna(
        subset=[
            "caller_person_id",
            "receiver_person_id",
        ]
    )

    # --------------------------------------------------
    # Communication features
    # --------------------------------------------------

    outgoing = (
        cdr.groupby(
            "caller_person_id"
        )
        .agg(
            total_outgoing_calls=(
                "cdr_id",
                "count",
            ),
            unique_contacts=(
                "to_phone",
                "nunique",
            ),
            total_call_duration=(
                "duration_seconds",
                "sum",
            ),
            average_call_duration=(
                "duration_seconds",
                "mean",
            ),
        )
        .reset_index()
        .rename(
            columns={
                "caller_person_id":
                    "person_id"
            }
        )
    )

    incoming = (
        cdr.groupby(
            "receiver_person_id"
        )
        .agg(
            total_incoming_calls=(
                "cdr_id",
                "count",
            ),
            unique_callers=(
                "from_phone",
                "nunique",
            ),
        )
        .reset_index()
        .rename(
            columns={
                "receiver_person_id":
                    "person_id"
            }
        )
    )

    # --------------------------------------------------
    # Communication burst feature
    # --------------------------------------------------

    cdr["timestamp"] = pd.to_datetime(
        cdr["timestamp"]
    )

    # Number of outgoing calls per person per day.
    daily_calls = (
        cdr.groupby(
            [
                "caller_person_id",
                cdr["timestamp"].dt.date,
            ]
        )
        .size()
        .reset_index(
            name="daily_call_count"
        )
        .rename(
            columns={
                "caller_person_id":
                    "person_id",
                "timestamp":
                    "activity_date",
            }
        )
    )

    burst_features = (
        daily_calls.groupby(
            "person_id"
        )
        .agg(
            max_daily_calls=(
                "daily_call_count",
                "max",
            ),
            average_daily_calls=(
                "daily_call_count",
                "mean",
            ),
            active_days=(
                "activity_date",
                "nunique",
            ),
        )
        .reset_index()
    )

    # --------------------------------------------------
    # Night-time activity
    # --------------------------------------------------

    cdr["hour"] = cdr[
        "timestamp"
    ].dt.hour

    nighttime = cdr[
        cdr["hour"].between(
            22,
            23
        )
        | cdr["hour"].between(
            0,
            5
        )
    ]

    nighttime_features = (
        nighttime.groupby(
            "caller_person_id"
        )
        .agg(
            nighttime_calls=(
                "cdr_id",
                "count",
            )
        )
        .reset_index()
        .rename(
            columns={
                "caller_person_id":
                    "person_id"
            }
        )
    )

    # --------------------------------------------------
    # Financial features
    # --------------------------------------------------

    account_to_person = dict(
        zip(
            account_ownership[
                "account_id"
            ],
            account_ownership[
                "person_id"
            ],
        )
    )

    financial["sender_person_id"] = (
        financial[
            "from_account"
        ].map(account_to_person)
    )

    financial["receiver_person_id"] = (
        financial[
            "to_account"
        ].map(account_to_person)
    )

    sent_financial = (
        financial.dropna(
            subset=[
                "sender_person_id"
            ]
        )
        .groupby(
            "sender_person_id"
        )
        .agg(
            outgoing_transactions=(
                "transaction_id",
                "count",
            ),
            outgoing_amount=(
                "amount",
                "sum",
            ),
        )
        .reset_index()
        .rename(
            columns={
                "sender_person_id":
                    "person_id"
            }
        )
    )

    received_financial = (
        financial.dropna(
            subset=[
                "receiver_person_id"
            ]
        )
        .groupby(
            "receiver_person_id"
        )
        .agg(
            incoming_transactions=(
                "transaction_id",
                "count",
            ),
            incoming_amount=(
                "amount",
                "sum",
            ),
        )
        .reset_index()
        .rename(
            columns={
                "receiver_person_id":
                    "person_id"
            }
        )
    )

    # --------------------------------------------------
    # Surveillance features
    # --------------------------------------------------

    surveillance_features = (
        surveillance.groupby(
            "person_id"
        )
        .agg(
            observation_count=(
                "surveillance_id",
                "count",
            ),
            unique_locations=(
                "location_id",
                "nunique",
            ),
            unique_vehicles=(
                "vehicle_id",
                "nunique",
            ),
        )
        .reset_index()
    )

    # --------------------------------------------------
    # Network features from Neo4j
    # --------------------------------------------------

    graph_features = load_graph_features()

    # --------------------------------------------------
    # Merge everything
    # --------------------------------------------------

    features = persons[
        [
            "person_id",
            "name",
        ]
    ].copy()

    features = features.rename(
        columns={
            "name": "person_name"
        }
    )

    dataframes = [
        outgoing,
        incoming,
        burst_features,
        nighttime_features,
        sent_financial,
        received_financial,
        surveillance_features,
        graph_features,
    ]

    for dataframe in dataframes:

        features = features.merge(
            dataframe,
            on="person_id",
            how="left",
            suffixes=(
                "",
                "_graph",
            ),
        )

    # Remove duplicate name columns if graph_features
    # introduced them.
    features = features.drop(
        columns=[
            column
            for column in [
                "person_name_graph"
            ]
            if column in features.columns
        ]
    )

    # --------------------------------------------------
    # Fill missing activity with zero.
    # --------------------------------------------------

    numeric_columns = (
        features.select_dtypes(
            include="number"
        )
        .columns
    )

    features[numeric_columns] = (
        features[numeric_columns]
        .fillna(0)
    )

    # Explicit derived features
    features[
        "total_calls"
    ] = (
        features[
            "total_outgoing_calls"
        ]
        + features[
            "total_incoming_calls"
        ]
    )

    features[
        "total_transactions"
    ] = (
        features[
            "outgoing_transactions"
        ]
        + features[
            "incoming_transactions"
        ]
    )

    features[
        "total_financial_amount"
    ] = (
        features[
            "outgoing_amount"
        ]
        + features[
            "incoming_amount"
        ]
    )

    # Save
    features.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        "NEXUS anomaly feature engineering completed."
    )

    print(
        f"Entities: {len(features)}"
    )

    print(
        f"Output: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()