import os
import pandas as pd
from typing import Tuple

REQUIRED_COLUMNS = {
    "surgery_id",
    "timestamp",
    "channel",
    "values",
    "stimulus",
    "signal_rate",
    "baseline_timestamp",
    "baseline_values",
    "baseline_stimulus",
    "baseline_signal_rate",
}


def load_signals(pkl_path: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load monitoring signals from a pickle file.

    Parameters
    ----------
    pkl_path: str
        Path to the pickle file produced by the data-collection pipeline.

    Returns
    -------
    Tuple containing four pandas DataFrames in the following order:
        mep_df, ssep_upper_df, ssep_lower_df, surgery_meta_df

    Raises
    ------
    FileNotFoundError
        If the given path does not exist.
    KeyError
        If expected keys or columns are missing from the pickle.
    """
    if not os.path.isfile(pkl_path):
        raise FileNotFoundError(f"Pickle file not found: {pkl_path}")

    data = pd.read_pickle(pkl_path)

    if not isinstance(data, dict):
        raise KeyError("Pickle file must contain a dictionary with the expected keys")

    # Some versions of the pipeline used '_surgerydata' as the key name.
    if 'surgerydata' not in data and '_surgerydata' in data:
        data['surgerydata'] = data['_surgerydata']

    expected_keys = ['mep_data', 'ssep_upper_data', 'ssep_lower_data', 'surgerydata']
    missing_keys = [k for k in expected_keys if k not in data]
    if missing_keys:
        raise KeyError(f"Missing keys in pickle: {', '.join(missing_keys)}")

    mep_df = data['mep_data']
    ssep_upper_df = data['ssep_upper_data']
    ssep_lower_df = data['ssep_lower_data']
    surgery_meta = data['surgerydata']

    for name, df in {
        'mep_data': mep_df,
        'ssep_upper_data': ssep_upper_df,
        'ssep_lower_data': ssep_lower_df,
    }.items():
        if not isinstance(df, pd.DataFrame):
            raise KeyError(f"'{name}' is not a pandas DataFrame")
        missing_cols = REQUIRED_COLUMNS - set(df.columns)
        if missing_cols:
            raise KeyError(f"DataFrame '{name}' missing required columns: {', '.join(sorted(missing_cols))}")

    if isinstance(surgery_meta, dict):
        surgery_meta_df = pd.DataFrame.from_dict(surgery_meta, orient='index')
    elif isinstance(surgery_meta, pd.DataFrame):
        surgery_meta_df = surgery_meta
    else:
        raise KeyError("'surgerydata' must be a dict or DataFrame")

    return mep_df, ssep_upper_df, ssep_lower_df, surgery_meta_df


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage: python data_loader.py <path_to_pickle>")
    else:
        paths = load_signals(sys.argv[1])
        names = ["mep", "ssep_upper", "ssep_lower", "surgery_meta"]
        for name, df in zip(names, paths):
            print(f"{name}: {df.shape}")

