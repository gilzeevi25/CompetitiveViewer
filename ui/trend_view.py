import pandas as pd
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QRadioButton,
    QButtonGroup,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QTabWidget,
)
from PyQt5.QtCore import Qt
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
        self.mep_radio.toggled.connect(self._populate_channels)
        self.mep_radio.toggled.connect(self.update_view)
        self.ssep_radio.toggled.connect(self._populate_channels)
        self.ssep_radio.toggled.connect(self.update_view)
        radio_layout.addWidget(self.mep_radio)
        radio_layout.addWidget(self.ssep_radio)
        layout.addLayout(radio_layout)

        # Channel picker
        self.channel_list = QListWidget()
        self.channel_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.channel_list.itemChanged.connect(self.update_view)
        layout.addWidget(self.channel_list)

        # Tabbed plots
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.channel_plots = pg.GraphicsLayoutWidget()
        self.tabs.addTab(self.channel_plots, "Channels")

        self.summary_plot = BasePlotWidget()
        self.summary_legend = self.summary_plot.plotItem.legend
        self.tabs.addTab(self.summary_plot, "Summary")
        self.tabs.currentChanged.connect(self.update_view)

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
        self._populate_channels()
        self.update_view()

    def set_channel_order(self, channels: list) -> None:
        """Update the channel ordering used for plotting."""
        self._channel_order = list(channels)
        self._populate_channels()
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

    def _populate_channels(self) -> None:
        """Fill the channel list based on available data."""
        df = self._current_dataframe()
        channels = []
        if df is not None and not df.empty:
            channels = list(df["channel"].unique())
        if self._channel_order:
            ordered = [c for c in self._channel_order if c in channels]
            for c in channels:
                if c not in ordered:
                    ordered.append(c)
            channels = ordered
        else:
            channels = sorted(channels)

        self.channel_list.blockSignals(True)
        current_checks = {
            self.channel_list.item(i).text(): self.channel_list.item(i).checkState() == Qt.Checked
            for i in range(self.channel_list.count())
        }
        self.channel_list.clear()
        for ch in channels:
            item = QListWidgetItem(str(ch))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            state = Qt.Checked if current_checks.get(str(ch), True) else Qt.Unchecked
            item.setCheckState(state)
            self.channel_list.addItem(item)
        self.channel_list.blockSignals(False)

    def update_view(self) -> None:
        df = self._current_dataframe()
        self.channel_plots.clear()
        self.summary_plot.clear()
        if self.summary_legend is not None:
            self.summary_legend.clear()
        if df is None or df.empty:
            self.min_label.setText("Min: N/A")
            self.max_label.setText("Max: N/A")
            self.mean_label.setText("Mean: N/A")
            return

        p2p_df = calculate_p2p(df)

        selected_channels = [
            self.channel_list.item(i).text()
            for i in range(self.channel_list.count())
            if self.channel_list.item(i).checkState() == Qt.Checked
        ]

        if not selected_channels:
            self.min_label.setText("Min: N/A")
            self.max_label.setText("Max: N/A")
            self.mean_label.setText("Mean: N/A")
            return

        p2p_df = p2p_df[p2p_df["channel"].isin(selected_channels)]

        global_min = p2p_df["p2p"].min()
        global_max = p2p_df["p2p"].max()
        global_mean = p2p_df["p2p"].mean()
        self.min_label.setText(f"Min: {global_min:.2f}")
        self.max_label.setText(f"Max: {global_max:.2f}")
        self.mean_label.setText(f"Mean: {global_mean:.2f}")

        if self.tabs.currentIndex() == 0:
            first_plot = None
            for row, channel in enumerate(selected_channels):
                subset = p2p_df[p2p_df["channel"] == channel]
                plot = self.channel_plots.addPlot(row=row, col=0)
                plot.showGrid(x=True, y=True, alpha=0.3)
                color = pg.intColor(row, hues=len(selected_channels))
                plot.plot(
                    subset["timestamp"].to_list(),
                    subset["p2p"].to_list(),
                    pen=pg.mkPen(color, width=2),
                )
                plot.setLabel("left", str(channel))
                if first_plot is None:
                    first_plot = plot
                else:
                    plot.setXLink(first_plot)
        else:
            grouped = p2p_df.groupby("timestamp")["p2p"]
            max_vals = grouped.max()
            median_vals = grouped.median()
            min_vals = grouped.min()
            x = list(max_vals.index)
            self.summary_plot.plot(x, max_vals.values, pen=pg.mkPen("r", width=2), name="Max")
            self.summary_plot.plot(x, median_vals.values, pen=pg.mkPen("g", width=2), name="Median")
            self.summary_plot.plot(x, min_vals.values, pen=pg.mkPen("b", width=2), name="Min")


