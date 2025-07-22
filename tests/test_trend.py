import pytest
import pandas as pd
from ui.trend_view import calculate_l1


def test_calculate_l1_simple():
    max_amp = 4.0
    rows = []
    steps = 5
    for i in range(steps):
        a = max_amp * i / (steps - 1)
        rows.append({"timestamp": i, "channel": "ch", "values": [-a, a]})
    df = pd.DataFrame(rows)

    out = calculate_l1(df)

    assert out["l1"].max() == pytest.approx(max_amp * 2)
    assert out["l1"].min() == pytest.approx(0.0)
    assert out["l1"].mean() == pytest.approx(max_amp)
