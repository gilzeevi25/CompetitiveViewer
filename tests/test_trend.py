import pytest
import numpy as np
import pandas as pd
from ui.trend_view import calculate_l1


def test_calculate_l1_simple():
    amp = 2.0
    rows = []
    steps = 10
    for i in range(steps):
        a = amp * i / (steps - 1)
        values = [-a, a]
        rows.append({"timestamp": i, "channel": "ch", "values": values})
    df = pd.DataFrame(rows)
    out = calculate_l1(df)

    assert out["l1"].max() == pytest.approx(amp * 2, rel=1e-6)
    assert out["l1"].min() == pytest.approx(0, abs=1e-8)
    assert out["l1"].mean() == pytest.approx(amp, rel=1e-6)

