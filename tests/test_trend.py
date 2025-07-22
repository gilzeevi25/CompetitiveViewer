import pytest
import math
import pandas as pd
from ui.trend_view import calculate_l1_norm, calculate_p2p, calculate_rms


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


def test_calculate_p2p_sine():
    amp = 2.0
    rows = []
    steps = 10
    for i in range(steps):
        a = amp * i / (steps - 1)
        values = [math.sin(2 * math.pi * j / 49) * a for j in range(50)]
        rows.append({"timestamp": i, "channel": "ch", "values": values})
    df = pd.DataFrame(rows)
    out = calculate_p2p(df)

    assert out["p2p"].max() == pytest.approx(4.0, rel=1e-6)
    assert out["p2p"].min() == pytest.approx(0, abs=1e-8)


def test_calculate_rms_sine():
    amp = 2.0
    rows = []
    steps = 10
    for i in range(steps):
        a = amp * i / (steps - 1)
        values = [math.sin(2 * math.pi * j / 49) * a for j in range(50)]
        rows.append({"timestamp": i, "channel": "ch", "values": values})
    df = pd.DataFrame(rows)
    out = calculate_rms(df)

    assert out["rms"].max() == pytest.approx(1.4142, rel=1e-2)
    assert out["rms"].min() == pytest.approx(0, abs=1e-8)
