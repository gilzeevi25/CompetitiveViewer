import pandas as pd
from src import data_loader

REQUIRED = {"surgery_id", "channel", "timestamp", "values", "baseline_values", "signal_rate"}


def test_load_signals(tiny_pickle):
    mep, ssep_u, ssep_l, meta = data_loader.load_signals(tiny_pickle)

    for df in (mep, ssep_u, ssep_l, meta):
        assert isinstance(df, pd.DataFrame)

    for df in (mep, ssep_u, ssep_l):
        assert REQUIRED.issubset(df.columns)
