from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
)


ROOT = Path(__file__).resolve().parents[1]

RESULTS_PATH = (
    ROOT
    / "data"
    / "processed"
    / "anomalies"
    / "person_anomaly_results.csv"
)

GROUND_TRUTH_PATH = (
    ROOT
    / "data"
    / "ground_truth"
    / "anomalies"
    / "anomalies.csv"
)

PHONE_OWNERSHIP_PATH = (
    ROOT
    / "data"
    / "phone_ownership.csv"
)


def main() -> None:

    results = pd.read_csv(
        RESULTS_PATH
    )

    ground_truth = pd.read_csv(
        GROUND_TRUTH_PATH
    )

    ownership = pd.read_csv(
        PHONE_OWNERSHIP_PATH
    )

    # Ground-truth anomaly phones → people
    anomaly_phones = set(
        ground_truth[
            "entity_id"
        ]
    )

    anomaly_people = set(
        ownership[
            ownership[
                "phone_id"
            ].isin(anomaly_phones)
        ][
            "person_id"
        ]
    )

    results[
        "ground_truth_anomaly"
    ] = results[
        "person_id"
    ].isin(
        anomaly_people
    )

    y_true = results[
        "ground_truth_anomaly"
    ].astype(int)

    y_pred = results[
        "is_anomaly"
    ].astype(int)

    precision = precision_score(
        y_true,
        y_pred,
        zero_division=0,
    )

    recall = recall_score(
        y_true,
        y_pred,
        zero_division=0,
    )

    f1 = f1_score(
        y_true,
        y_pred,
        zero_division=0,
    )

    matrix = confusion_matrix(
        y_true,
        y_pred,
    )

    print(
        "NEXUS anomaly detection evaluation"
    )

    print(
        f"Ground-truth anomaly people: "
        f"{sorted(anomaly_people)}"
    )

    print(
        f"Precision: {precision:.4f}"
    )

    print(
        f"Recall: {recall:.4f}"
    )

    print(
        f"F1: {f1:.4f}"
    )

    print(
        "Confusion matrix:"
    )

    print(matrix)


if __name__ == "__main__":
    main()
    