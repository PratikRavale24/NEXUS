from __future__ import annotations

import pandas as pd
from sklearn.ensemble import IsolationForest


def test_anomaly_model_produces_results():

    dataframe = pd.DataFrame(
        {
            "total_calls": [10, 11, 9, 12, 200],
            "unique_contacts": [3, 4, 3, 4, 25],
            "max_daily_calls": [4, 5, 4, 5, 100],
        }
    )

    model = IsolationForest(
        n_estimators=200,
        contamination="auto",
        random_state=42,
    )

    model.fit(dataframe)

    scores = model.score_samples(
        dataframe
    )

    predictions = model.predict(
        dataframe
    )

    assert len(scores) == 5
    assert len(predictions) == 5
    assert set(predictions).issubset(
        {-1, 1}
    )