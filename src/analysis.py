import numpy as np
import pandas as pd


def calculate_l1_norm(df: pd.DataFrame) -> pd.DataFrame:
    """Compute L1 norm of the signal for each timestamp/channel row."""
    if df is None or df.empty:
        return pd.DataFrame(columns=["timestamp", "channel", "l1"])

    result = df[["timestamp", "channel", "values"]].copy()

    def _l1(arr):
        np_arr = np.asarray(arr, dtype=float)
        return float(np.sum(np.abs(np_arr))) if np_arr.size > 0 else 0.0

    result["l1"] = result["values"].apply(_l1)
    return result[["timestamp", "channel", "l1"]]
