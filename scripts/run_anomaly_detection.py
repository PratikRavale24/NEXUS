from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest


ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    ROOT
    / "data"
    / "processed"
    / "anomalies"
    / "person_anomaly_features.csv"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "processed"
    / "anomalies"
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "person_anomaly_results.csv"
)

MODEL_COLUMNS = [
    "total_outgoing_calls",
    "unique_contacts",
    "total_call_duration",
    "average_call_duration",
    "total_incoming_calls",
    "unique_callers",
    "max_daily_calls",
    "average_daily_calls",
    "nighttime_calls",
    "outgoing_transactions",
    "outgoing_amount",
    "incoming_transactions",
    "incoming_amount",
    "observation_count",
    "unique_locations",
    "unique_vehicles",
    "degree",
    "betweenness",
    "pagerank",
    "total_calls",
    "total_transactions",
    "total_financial_amount",
]


def main() -> None:

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    dataframe = pd.read_csv(
        INPUT_PATH
    )

    # --------------------------------------------------
    # Prepare model input
    # --------------------------------------------------

    X = dataframe[
        MODEL_COLUMNS
    ].fillna(0)

    # --------------------------------------------------
    # Isolation Forest
    # --------------------------------------------------

    model = IsolationForest(
        n_estimators=300,
        max_samples="auto",
        contamination="auto",
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X)

    # Lower score_samples values indicate more
    # abnormal observations in scikit-learn.
    dataframe[
        "anomaly_score"
    ] = model.score_samples(X)

    dataframe[
        "anomaly_label"
    ] = model.predict(X)

    dataframe[
        "is_anomaly"
    ] = (
        dataframe["anomaly_label"]
        == -1
    )

    # Convert to an intuitive ranking where a
    # larger value means "more anomalous".
    dataframe[
        "anomaly_rank_score"
    ] = -dataframe[
        "anomaly_score"
    ]

    # --------------------------------------------------
    # Explainability metadata
    # --------------------------------------------------

    dataframe[
        "model"
    ] = "IsolationForest"

    dataframe[
        "feature_count"
    ] = len(MODEL_COLUMNS)

    # Rank the entities.
    dataframe = dataframe.sort_values(
        "anomaly_rank_score",
        ascending=False,
    )

    dataframe[
        "anomaly_rank"
    ] = range(
        1,
        len(dataframe) + 1,
    )

    dataframe.to_csv(
        OUTPUT_PATH,
        index=False,
    )

    print(
        "NEXUS anomaly detection completed."
    )

    print(
        f"Entities analysed: {len(dataframe)}"
    )

    print(
        "Detected anomalies:",
        int(
            dataframe[
                "is_anomaly"
            ].sum()
        ),
    )

    print(
        f"Results: {OUTPUT_PATH}"
    )

    print(
        "\nTop anomaly candidates:"
    )

    print(
        dataframe[
            [
                "anomaly_rank",
                "person_id",
                "person_name",
                "anomaly_rank_score",
                "is_anomaly",
            ]
        ]
        .head(10)
        .to_string(
            index=False
        )
    )


if __name__ == "__main__":
    main()