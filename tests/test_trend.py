import pytest
import numpy as np
import pandas as pd
from ui.trend_view import calculate_p2p


def test_calculate_p2p_sine():
    amp = 2.0
    rows = []
    steps = 10
    for i in range(steps):
        a = amp * i / (steps - 1)
        values = np.sin(np.linspace(0, 2 * np.pi, 50)) * a
        rows.append({"timestamp": i, "channel": "ch", "values": values})
    df = pd.DataFrame(rows)
    out = calculate_p2p(df)

    assert out["p2p"].max() == pytest.approx(amp * 2, rel=1e-2)
    assert out["p2p"].min() == pytest.approx(0, abs=1e-8)
    assert out["p2p"].mean() == pytest.approx(amp, rel=1e-2)
