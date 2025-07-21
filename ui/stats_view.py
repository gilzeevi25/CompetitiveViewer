import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QRadioButton,
    QButtonGroup,
    QLabel,
)
import pyqtgraph as pg

from .plot_widgets import BasePlotWidget


def _aggregate_signals(values: list, func) -> list:
    if not values:
        return []
    max_len = max(len(v) for v in values)
    arr = np.full((len(values), max_len), np.nan)
    for i, v in enumerate(values):
        arr[i, : len(v)] = v
    return func(arr, axis=0)


class StatsView(QWidget):
    """Plot median/mean/max of signals across channels."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mep_df = None
        self.ssep_upper_df = None
        self.ssep_lower_df = None

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        radio_layout = QHBoxLayout()
        self.mep_radio = QRadioButton("MEP")
        self.ssep_radio = QRadioButton("SSEP")
        self.mep_radio.setChecked(True)
        group = QButtonGroup(self)
        group.addButton(self.mep_radio)
        group.addButton(self.ssep_radio)
        self.mep_radio.toggled.connect(self.update_view)
        self.ssep_radio.toggled.connect(self.update_view)
        radio_layout.addWidget(self.mep_radio)
        radio_layout.addWidget(self.ssep_radio)
        layout.addLayout(radio_layout)

        self.plot = BasePlotWidget()
        layout.addWidget(self.plot)

    def refresh(self, data_dict: dict) -> None:
        self.mep_df = data_dict.get("mep_df")
        self.ssep_upper_df = data_dict.get("ssep_upper_df")
        self.ssep_lower_df = data_dict.get("ssep_lower_df")
        self.update_view()

    def _current_dataframe(self) -> pd.DataFrame:
        if self.mep_radio.isChecked():
            return self.mep_df
        frames = []
        if self.ssep_upper_df is not None:
            frames.append(self.ssep_upper_df)
        if self.ssep_lower_df is not None:
            frames.append(self.ssep_lower_df)
        if frames:
            return pd.concat(frames, ignore_index=True)
        return None

    def update_view(self) -> None:
        df = self._current_dataframe()
        self.plot.clear()
        if df is None or df.empty:
            return

        values = df["values"].to_list()
        mean = _aggregate_signals(values, np.nanmean)
        median = _aggregate_signals(values, np.nanmedian)
        max_vals = _aggregate_signals(values, np.nanmax)
        x = list(range(len(mean)))
        self.plot.plot(x, mean, pen=pg.mkPen("y", width=2), name="Mean")
        self.plot.plot(x, median, pen=pg.mkPen("c", width=2), name="Median")
        self.plot.plot(x, max_vals, pen=pg.mkPen("m", width=2), name="Max")

