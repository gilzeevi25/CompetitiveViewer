from pathlib import Path

import numpy as np
import pandas as pd
import pytest

@pytest.fixture
def tiny_pickle(tmp_path: Path) -> str:
    """Create a tiny pickle with minimal valid data and return its path."""
    n = 5

    def make_df(prefix: str) -> pd.DataFrame:
        data = {
            "surgery_id": ["S1"] * n,
            "timestamp": list(range(n)),
            "channel": [f"{prefix}{i}" for i in range(n)],
            "values": [list(np.sin(np.linspace(0, np.pi, 5))) for _ in range(n)],
            "stimulus": [{}] * n,
            "signal_rate": [1000] * n,
            "baseline_timestamp": [0] * n,
            "baseline_values": [list(np.zeros(5)) for _ in range(n)],
            "baseline_stimulus": [{}] * n,
            "baseline_signal_rate": [1000] * n,
        }
        return pd.DataFrame(data)

    mep_df = make_df("M")
    ssep_upper_df = make_df("U")
    ssep_lower_df = make_df("L")
    surgery_meta = {"S1": {"date": "2021-01-01", "protocol": "test"}}

    data = {
        "mep_data": mep_df,
        "ssep_upper_data": ssep_upper_df,
        "ssep_lower_data": ssep_lower_df,
        "surgerydata": surgery_meta,
    }

    pkl_path = tmp_path / "tiny.pkl"
    pd.to_pickle(data, pkl_path)
    return str(pkl_path)
