import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QRadioButton,
    QButtonGroup,
    QLabel,
    QScrollArea,
    QGridLayout,
)
import pyqtgraph as pg

from .plot_widgets import BasePlotWidget


def calculate_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Compute mean, median and max for each timestamp/channel row."""
    if df is None or df.empty:
        return pd.DataFrame(columns=["timestamp", "channel", "mean", "median", "max"])

    result = df[["timestamp", "channel", "values"]].copy()
    result["mean"] = result["values"].apply(lambda arr: float(np.mean(arr)) if len(arr) > 0 else 0)
    result["median"] = result["values"].apply(lambda arr: float(np.median(arr)) if len(arr) > 0 else 0)
    result["max"] = result["values"].apply(lambda arr: max(arr) if len(arr) > 0 else 0)
    return result[["timestamp", "channel", "mean", "median", "max"]]


class StatsView(QWidget):
    """Widget for displaying mean/median/max stats across time."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.mep_df = None
        self.ssep_upper_df = None
        self.ssep_lower_df = None
        self._channel_order = []
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

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.plot_container = QWidget()
        self.grid = QGridLayout(self.plot_container)
        self.scroll.setWidget(self.plot_container)
        layout.addWidget(self.scroll)

        stats_layout = QHBoxLayout()
        self.min_label = QLabel("Min: N/A")
        self.max_label = QLabel("Max: N/A")
        self.mean_label = QLabel("Mean: N/A")
        stats_layout.addWidget(self.min_label)
        stats_layout.addWidget(self.max_label)
        stats_layout.addWidget(self.mean_label)
        layout.addLayout(stats_layout)

        self.plots = []

    def refresh(self, data_dict: dict) -> None:
        self.mep_df = data_dict.get("mep_df")
        self.ssep_upper_df = data_dict.get("ssep_upper_df")
        self.ssep_lower_df = data_dict.get("ssep_lower_df")
        self.update_view()

    def set_channel_order(self, channels: list) -> None:
        self._channel_order = list(channels)
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

    def _create_plots(self, channels: list) -> None:
        for plt in self.plots:
            plt.setParent(None)
        self.plots = []
        for idx, _ in enumerate(channels):
            plot = BasePlotWidget()
            plot.addLegend(offset=(10, 10))
            row = idx // 2
            col = idx % 2
            self.grid.addWidget(plot, row, col)
            self.plots.append(plot)

    def update_view(self, channels_filter=None) -> None:
        df = self._current_dataframe()
        if df is None or df.empty:
            for plt in self.plots:
                plt.clear()
            self.min_label.setText("Min: N/A")
            self.max_label.setText("Max: N/A")
            self.mean_label.setText("Mean: N/A")
            return

        stats_df = calculate_stats(df)
        if channels_filter is not None:
            stats_df = stats_df[stats_df["channel"].isin(channels_filter)]
        channels = list(stats_df["channel"].unique())
        if self._channel_order:
            ordered = [ch for ch in self._channel_order if ch in channels]
            for ch in channels:
                if ch not in ordered:
                    ordered.append(ch)
            channels = ordered
        else:
            channels = sorted(channels)

        self._create_plots(channels)

        global_min = stats_df[["mean", "median", "max"]].min().min()
        global_max = stats_df[["mean", "median", "max"]].max().max()
        global_mean = stats_df[["mean", "median", "max"]].mean().mean()
        self.min_label.setText(f"Min: {global_min:.2f}")
        self.max_label.setText(f"Max: {global_max:.2f}")
        self.mean_label.setText(f"Mean: {global_mean:.2f}")

        for idx, channel in enumerate(channels):
            subset = stats_df[stats_df["channel"] == channel]
            x = subset["timestamp"].to_list()
            means = subset["mean"].to_list()
            medians = subset["median"].to_list()
            maxs = subset["max"].to_list()
            plot = self.plots[idx]
            plot.clear()
            legend = plot.plotItem.legend
            if legend is not None:
                legend.clear()
            plot.plot(x, means, pen=pg.mkPen("y", width=2), name="Mean")
            plot.plot(x, medians, pen=pg.mkPen("c", width=2), name="Median")
            plot.plot(x, maxs, pen=pg.mkPen("m", width=2), name="Max")
            plot.setTitle(str(channel))
