import numpy as np
import pandas as pd
from ui.trend_view import calculate_l1_norm
import pytest


def test_calculate_l1_norm_sine():
    amp = 2.0
    rows = []
    steps = 10
    for i in range(steps):
        a = amp * i / (steps - 1)
        values = np.sin(np.linspace(0, 2 * np.pi, 50)) * a
        rows.append({"timestamp": i, "channel": "ch", "values": values})
    df = pd.DataFrame(rows)
    out = calculate_l1_norm(df)

    expected = [float(np.sum(np.abs(v))) for v in df["values"]]
    assert out["l1"].tolist() == pytest.approx(expected)
