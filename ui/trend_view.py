import pandas as pd
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QComboBox,
    QLabel,
)
import pyqtgraph as pg
from .plot_widgets import BasePlotWidget


def calculate_l1_norm(df: pd.DataFrame) -> pd.DataFrame:
    """Compute L1 norm of the signal for each timestamp/channel row."""
    if df is None or df.empty:
        return pd.DataFrame(columns=["timestamp", "channel", "l1"])

    result = df[["timestamp", "channel", "values"]].copy()
    result["l1"] = result["values"].apply(
        lambda arr: float(sum(abs(v) for v in arr)) if len(arr) > 0 else 0.0
    )
    return result[["timestamp", "channel", "l1"]]


def calculate_p2p(df: pd.DataFrame) -> pd.DataFrame:
    """Compute peak-to-peak amplitude for each timestamp/channel row."""
    if df is None or df.empty:
        return pd.DataFrame(columns=["timestamp", "channel", "p2p"])

    result = df[["timestamp", "channel", "values"]].copy()
    result["p2p"] = result["values"].apply(
        lambda arr: float(max(arr) - min(arr)) if len(arr) > 0 else 0.0
    )
    return result[["timestamp", "channel", "p2p"]]


def calculate_rms(df: pd.DataFrame) -> pd.DataFrame:
    """Compute RMS of the signal for each timestamp/channel row."""
    if df is None or df.empty:
        return pd.DataFrame(columns=["timestamp", "channel", "rms"])

    result = df[["timestamp", "channel", "values"]].copy()
    result["rms"] = result["values"].apply(
        lambda arr: float((sum(v * v for v in arr) / len(arr)) ** 0.5)
        if len(arr) > 0
        else 0.0
    )
    return result[["timestamp", "channel", "rms"]]





class TrendView(QWidget):
    """Widget for displaying L1-norm trends across time."""

    modalityChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.mep_df = None
        self.ssep_upper_df = None
        self.ssep_lower_df = None
        self._surgery_id = None
        self._channel_order = []

        self._visible_channels = []
        self._channel_plots = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Modality selector
        selector_layout = QHBoxLayout()
        selector_layout.addWidget(QLabel("Modality:"))
        self.modality_combo = QComboBox()
        self.modality_combo.addItems(["MEP", "SSEP_UPPER", "SSEP_LOWER"])
        self.modality_combo.currentTextChanged.connect(self.update_view)
        self.modality_combo.currentTextChanged.connect(self.modalityChanged.emit)
        selector_layout.addWidget(self.modality_combo)
        selector_layout.addStretch(1)
        layout.addLayout(selector_layout)

        # Trend method selector
        method_layout = QHBoxLayout()
        method_layout.addWidget(QLabel("Method:"))
        self.method_combo = QComboBox()
        self.method_combo.addItems(["L1", "P2P", "RMS"])
        self.method_combo.currentTextChanged.connect(self.update_view)
        method_layout.addWidget(self.method_combo)
        method_layout.addStretch(1)
        layout.addLayout(method_layout)

        # Layout for channel plots
        self.channel_grid = QGridLayout()
        self.channel_grid.setColumnStretch(0, 1)
        self.channel_grid.setColumnStretch(1, 1)
        layout.addLayout(self.channel_grid)

        # Global summary plot
        self.global_plot = BasePlotWidget(self)
        self.global_legend = self.global_plot.plotItem.legend
        layout.addWidget(self.global_plot)

    def refresh(self, data_dict: dict) -> None:
        """Update internal data and refresh the display."""
        self.mep_df = data_dict.get("mep_df")
        self.ssep_upper_df = data_dict.get("ssep_upper_df")
        self.ssep_lower_df = data_dict.get("ssep_lower_df")
        self.update_view()

    def set_current_surgery(self, surgery_id: str) -> None:
        """Set surgery context for filtering."""
        self._surgery_id = surgery_id
        self.update_view()

    def set_channel_order(self, channels: list) -> None:
        """Update the channel ordering used for plotting."""
        self._channel_order = list(channels)
        self.update_view()

    def set_visible_channels(self, channels: list) -> None:
        """Set which channels should be displayed."""
        self._visible_channels = list(channels)

    # -----------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------
    def _current_dataframe(self) -> pd.DataFrame:
        mode = self.modality_combo.currentText()
        if mode == "MEP":
            return self.mep_df
        if mode == "SSEP_UPPER":
            return self.ssep_upper_df
        if mode == "SSEP_LOWER":
            return self.ssep_lower_df
        return None

    def update_view(self, *args, end_timestamp=None) -> None:
        df = self._current_dataframe()
        if df is not None and self._surgery_id is not None:
            df = df[df["surgery_id"] == self._surgery_id]
        if end_timestamp is not None and df is not None and not df.empty:
            df = df[df["timestamp"] <= end_timestamp]
        # clear layout positions without deleting widgets
        while self.channel_grid.count():
            self.channel_grid.takeAt(0)

        self.global_plot.clear()
        if self.global_legend is not None:
            self.global_legend.clear()

        if df is None or df.empty:
            return

        method = self.method_combo.currentText()
        if method == "L1":
            norm_df = calculate_l1_norm(df)
            value_col = "l1"
        elif method == "P2P":
            norm_df = calculate_p2p(df)
            value_col = "p2p"
        else:
            norm_df = calculate_rms(df)
            value_col = "rms"

        unique_channels = list(norm_df["channel"].unique())
        if self._channel_order:
            channels = [ch for ch in self._channel_order if ch in unique_channels]
            for ch in unique_channels:
                if ch not in channels:
                    channels.append(ch)
        else:
            channels = sorted(unique_channels)

        if self._visible_channels:
            channels = [ch for ch in channels if ch in self._visible_channels]

        left_row = right_row = 0
        used = set()
        used_cols = {0: False, 1: False}
        for channel in channels:
            subset = norm_df[norm_df["channel"] == channel]
            if subset.empty:
                continue
            x = subset["timestamp"].to_list()
            y = subset[value_col].to_list()

            if channel not in self._channel_plots:
                self._channel_plots[channel] = BasePlotWidget(self)
            plot = self._channel_plots[channel]
            plot.clear()
            plot.plot(x, y, pen=pg.mkPen(width=2))

            title = str(channel)
            mode = self.modality_combo.currentText()
            if mode == "SSEP_UPPER":
                title = f"Upper: {channel}"
            elif mode == "SSEP_LOWER":
                title = f"Lower: {channel}"
            plot.plotItem.setTitle(title)

            if str(channel).lower().startswith("r"):
                col = 1
                row = right_row
                right_row += 1
            else:
                col = 0
                row = left_row
                left_row += 1
            used_cols[col] = True

            self.channel_grid.addWidget(plot, row, col)
            plot.show()
            used.add(channel)

        # hide unused plots
        for ch, widget in self._channel_plots.items():
            if ch not in used:
                widget.hide()

        # adjust column stretch depending on which columns contain widgets
        if used_cols[0] and used_cols[1]:
            self.channel_grid.setColumnStretch(0, 1)
            self.channel_grid.setColumnStretch(1, 1)
        elif used_cols[0]:
            self.channel_grid.setColumnStretch(0, 1)
            self.channel_grid.setColumnStretch(1, 0)
        elif used_cols[1]:
            self.channel_grid.setColumnStretch(0, 0)
            self.channel_grid.setColumnStretch(1, 1)
        else:
            self.channel_grid.setColumnStretch(0, 1)
            self.channel_grid.setColumnStretch(1, 0)

        # Global statistics
        summary = norm_df.groupby("timestamp")[value_col].agg(["min", "max", "mean"])
        x_vals = summary.index.to_list()
        self.global_plot.plot(x_vals, summary["min"].to_list(), pen=pg.mkPen("y", width=2), name="Min")
        self.global_plot.plot(x_vals, summary["max"].to_list(), pen=pg.mkPen("r", width=2), name="Max")
        self.global_plot.plot(x_vals, summary["mean"].to_list(), pen=pg.mkPen("c", width=2), name="Avg")

