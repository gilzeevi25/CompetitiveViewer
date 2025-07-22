import pytest
import math
import pandas as pd
from ui.trend_view import calculate_l1_norm


def test_calculate_l1_norm_sine():
    amp = 2.0
    rows = []
    steps = 10
    for i in range(steps):
        a = amp * i / (steps - 1)
        values = [math.sin(2 * math.pi * j / 49) * a for j in range(50)]
        rows.append({"timestamp": i, "channel": "ch", "values": values})
    df = pd.DataFrame(rows)
    out = calculate_l1_norm(df)

    assert out["l1"].max() == pytest.approx(62.367, rel=1e-2)
    assert out["l1"].min() == pytest.approx(0, abs=1e-8)
    assert out["l1"].mean() == pytest.approx(31.1837, rel=1e-2)
