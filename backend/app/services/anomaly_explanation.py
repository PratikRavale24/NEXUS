from __future__ import annotations

import pandas as pd


def explain_anomaly(
    row: pd.Series,
    percentile_table: dict[str, float],
) -> list[str]:

    reasons: list[str] = []

    feature_rules = [
        (
            "total_outgoing_calls",
            "total outgoing communication volume",
        ),
        (
            "unique_contacts",
            "number of unique communication contacts",
        ),
        (
            "max_daily_calls",
            "maximum calls observed within a day",
        ),
        (
            "nighttime_calls",
            "night-time communication activity",
        ),
        (
            "total_transactions",
            "number of financial transactions",
        ),
        (
            "total_financial_amount",
            "aggregate financial activity",
        ),
        (
            "degree",
            "network connectivity",
        ),
        (
            "betweenness",
            "bridge-position in the network",
        ),
    ]

    for feature, label in feature_rules:

        value = float(
            row.get(
                feature,
                0,
            )
        )

        percentile = percentile_table.get(
            feature,
            0.0,
        )

        if percentile >= 0.95:

            reasons.append(
                f"High {label}: "
                f"{value:.2f} "
                f"(top {100 - percentile * 100:.1f}% "
                f"of observed entities)."
            )

        elif percentile >= 0.90:

            reasons.append(
                f"Elevated {label}: "
                f"{value:.2f}."
            )

    if not reasons:

        reasons.append(
            "The model identified an unusual "
            "multi-feature behavioral profile."
        )

    return reasons