import pandas as pd
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QRadioButton,
    QButtonGroup,
    QLabel,
    QScrollArea,
)
import pyqtgraph as pg
from .plot_widgets import BasePlotWidget


def calculate_p2p(df: pd.DataFrame) -> pd.DataFrame:
    """Compute peak-to-peak amplitude for each timestamp/channel row."""
    if df is None or df.empty:
        return pd.DataFrame(columns=["timestamp", "channel", "p2p"])

    result = df[["timestamp", "channel", "values"]].copy()
    result["p2p"] = result["values"].apply(
        lambda arr: max(arr) - min(arr) if len(arr) > 0 else 0
    )
    return result[["timestamp", "channel", "p2p"]]


class TrendView(QWidget):
    """Widget for displaying peak-to-peak trends across time."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.mep_df = None
        self.ssep_upper_df = None
        self.ssep_lower_df = None
        self._channel_order = []
        self._selected_channels = []

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Radio buttons to select data source
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

        # Container for multiple plot widgets
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.plots_container = QWidget()
        self.plots_layout = QVBoxLayout(self.plots_container)
        self.scroll.setWidget(self.plots_container)
        layout.addWidget(self.scroll)
        self._plots = []

        # Stats labels
        stats_layout = QHBoxLayout()
        self.min_label = QLabel("Min: N/A")
        self.max_label = QLabel("Max: N/A")
        self.mean_label = QLabel("Mean: N/A")
        stats_layout.addWidget(self.min_label)
        stats_layout.addWidget(self.max_label)
        stats_layout.addWidget(self.mean_label)
        layout.addLayout(stats_layout)

    def refresh(self, data_dict: dict) -> None:
        """Update internal data and refresh the display."""
        self.mep_df = data_dict.get("mep_df")
        self.ssep_upper_df = data_dict.get("ssep_upper_df")
        self.ssep_lower_df = data_dict.get("ssep_lower_df")
        self.update_view()

    def set_channel_order(self, channels: list) -> None:
        """Update the channel ordering used for plotting."""
        self._channel_order = list(channels)
        self.update_view()

    def set_selected_channels(self, channels: list) -> None:
        """Specify which channels should be visible."""
        self._selected_channels = list(channels)
        self.update_view()

    # -----------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------
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

        # Remove existing plot widgets
        for plt in self._plots:
            plt.setParent(None)
        self._plots.clear()

        if df is None or df.empty:
            self.min_label.setText("Min: N/A")
            self.max_label.setText("Max: N/A")
            self.mean_label.setText("Mean: N/A")
            return

        if self._selected_channels:
            df = df[df["channel"].isin(self._selected_channels)]

        p2p_df = calculate_p2p(df)

        # Compute stats
        global_min = p2p_df["p2p"].min()
        global_max = p2p_df["p2p"].max()
        global_mean = p2p_df["p2p"].mean()
        self.min_label.setText(f"Min: {global_min:.2f}")
        self.max_label.setText(f"Max: {global_max:.2f}")
        self.mean_label.setText(f"Mean: {global_mean:.2f}")

        unique_channels = list(p2p_df["channel"].unique())
        if self._channel_order:
            channels = [ch for ch in self._channel_order if ch in unique_channels]
            for ch in unique_channels:
                if ch not in channels:
                    channels.append(ch)
        else:
            channels = sorted(unique_channels)

        for idx, channel in enumerate(channels):
            subset = p2p_df[p2p_df["channel"] == channel]
            x = subset["timestamp"].to_list()
            y = subset["p2p"].to_list()
            color = pg.intColor(idx, hues=len(channels))
            plt = BasePlotWidget()
            plt.plot(x, y, pen=pg.mkPen(color, width=2), name=str(channel))
            self.plots_layout.addWidget(plt)
            self._plots.append(plt)

