from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from backend.app.services.anomaly_explanation import (
    explain_anomaly,
)


ROOT = Path(__file__).resolve().parents[1]

INPUT_PATH = (
    ROOT
    / "data"
    / "processed"
    / "anomalies"
    / "person_anomaly_results.csv"
)

OUTPUT_PATH = (
    ROOT
    / "data"
    / "processed"
    / "anomalies"
    / "anomaly_explanations.json"
)

FEATURES = [
    "total_outgoing_calls",
    "unique_contacts",
    "max_daily_calls",
    "nighttime_calls",
    "total_transactions",
    "total_financial_amount",
    "degree",
    "betweenness",
]


def main() -> None:

    dataframe = pd.read_csv(
        INPUT_PATH
    )

    percentile_table = {}

    for feature in FEATURES:

        percentile_table[feature] = (
            dataframe[feature]
            .rank(
                pct=True,
                method="average",
            )
        )

    explanations = []

    for _, row in dataframe.iterrows():

        if not bool(
            row["is_anomaly"]
        ):
            continue

        percentiles = {
            feature: float(
                percentile_table[
                    feature
                ].loc[row.name]
            )
            for feature in FEATURES
        }

        reasons = explain_anomaly(
            row,
            percentiles,
        )

        explanations.append(
            {
                "person_id": row[
                    "person_id"
                ],
                "person_name": row[
                    "person_name"
                ],
                "anomaly_rank":
                    int(
                        row[
                            "anomaly_rank"
                        ]
                    ),
                "anomaly_score":
                    float(
                        row[
                            "anomaly_score"
                        ]
                    ),
                "reasons": reasons,
                "model": "IsolationForest",
            }
        )

    with OUTPUT_PATH.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            explanations,
            file,
            indent=2,
            ensure_ascii=False,
        )

    print(
        "Anomaly explanations generated."
    )

    print(
        f"Findings: {len(explanations)}"
    )

    print(
        f"Output: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    main()