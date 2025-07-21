import pandas as pd
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QRadioButton,
    QButtonGroup,
)
import pyqtgraph as pg
from .plot_widgets import BasePlotWidget
from .trend_view import calculate_p2p


class StatsView(QWidget):
    """Plot aggregated peak-to-peak statistics across time."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.mep_df = None
        self.ssep_upper_df = None
        self.ssep_lower_df = None
        self._selected_channels = []

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

    def set_selected_channels(self, channels: list) -> None:
        self._selected_channels = list(channels)
        self.update_view()

    def _current_dataframe(self) -> pd.DataFrame:
        if self.mep_radio.isChecked():
            return self.mep_df
        if self.ssep_radio.isChecked():
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

        if self._selected_channels:
            df = df[df["channel"].isin(self._selected_channels)]
        p2p_df = calculate_p2p(df)

        grouped = p2p_df.groupby("timestamp")["p2p"]
        mean = grouped.mean()
        median = grouped.median()
        max_ = grouped.max()

        x = mean.index.to_list()
        self.plot.plot(x, mean.to_list(), pen=pg.mkPen("#61AFEF", width=2), name="mean")
        self.plot.plot(x, median.to_list(), pen=pg.mkPen("#98C379", width=2), name="median")
        self.plot.plot(x, max_.to_list(), pen=pg.mkPen("#E06C75", width=2), name="max")
