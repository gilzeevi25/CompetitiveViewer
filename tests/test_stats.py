import pytest
import numpy as np
import pandas as pd
from ui.stats_view import calculate_stats


def test_calculate_stats_basic():
    rows = []
    for i in range(5):
        values = np.array([i, i + 1, i + 2])
        rows.append({"timestamp": i, "channel": "ch", "values": values})
    df = pd.DataFrame(rows)
    out = calculate_stats(df)
    assert list(out.columns) == ["timestamp", "channel", "mean", "median", "max"]
    assert out["mean"].iloc[0] == pytest.approx(np.mean([0, 1, 2]))
    assert out["median"].iloc[-1] == pytest.approx(np.median([4, 5, 6]))
    assert out["max"].iloc[2] == 4
