import numpy as np
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
)
import pyqtgraph as pg
from .plot_widgets import BasePlotWidget


def calculate_l1(df: pd.DataFrame) -> pd.DataFrame:
    """Compute L1 norm (sum of absolute values) for each row."""
    if df is None or df.empty:
        return pd.DataFrame(columns=["timestamp", "channel", "l1"])

    result = df[["timestamp", "channel", "values"]].copy()
    result["l1"] = result["values"].apply(
        lambda arr: float(np.sum(np.abs(arr))) if len(arr) > 0 else 0.0
    )
    return result[["timestamp", "channel", "l1"]]


class TrendView(QWidget):
    """Widget for displaying L1 norm trends across time."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.mep_df = None
        self.ssep_upper_df = None
        self.ssep_lower_df = None
        self._channel_order = []

        self._setup_ui()

    # --------------------------------------------------
    # UI setup
    # --------------------------------------------------
    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("Modality:"))
        self.modality_combo = QComboBox()
        self.modality_combo.addItems(["MEP", "SSEP_UPPER", "SSEP_LOWER"])
        self.modality_combo.currentTextChanged.connect(self.update_view)
        control_layout.addWidget(self.modality_combo)
        layout.addLayout(control_layout)

        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()
        plots_layout = QHBoxLayout()
        plots_layout.addLayout(self.left_layout)
        plots_layout.addLayout(self.right_layout)
        layout.addLayout(plots_layout)

        self.summary_plot = BasePlotWidget()
        layout.addWidget(self.summary_plot)

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------
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

    # --------------------------------------------------
    # Internal helpers
    # --------------------------------------------------
    def _current_dataframe(self) -> pd.DataFrame:
        mode = self.modality_combo.currentText()
        if mode == "MEP":
            return self.mep_df
        if mode == "SSEP_UPPER":
            return self.ssep_upper_df
        if mode == "SSEP_LOWER":
            return self.ssep_lower_df
        return None

    def _clear_plots(self) -> None:
        for layout in (self.left_layout, self.right_layout):
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        self.summary_plot.clear()
        legend = self.summary_plot.plotItem.legend
        if legend is not None:
            legend.clear()

    def update_view(self) -> None:
        self._clear_plots()
        df = self._current_dataframe()
        if df is None or df.empty:
            return

        l1_df = calculate_l1(df)
        unique_channels = list(l1_df["channel"].unique())
        if self._channel_order:
            channels = [c for c in self._channel_order if c in unique_channels]
            for ch in unique_channels:
                if ch not in channels:
                    channels.append(ch)
        else:
            channels = sorted(unique_channels)

        summary = {}
        for idx, channel in enumerate(channels):
            subset = l1_df[l1_df["channel"] == channel]
            if subset.empty:
                continue
            x = subset["timestamp"].to_list()
            y = subset["l1"].to_list()
            plot = BasePlotWidget()
            plot.plot(x, y, pen=pg.mkPen(pg.intColor(idx, hues=len(channels)), width=2))
            mode = self.modality_combo.currentText()
            title = channel
            if mode == "SSEP_UPPER":
                title = f"Upper: {channel}"
            elif mode == "SSEP_LOWER":
                title = f"Lower: {channel}"
            plot.plotItem.setTitle(title)
            target = self.right_layout if str(channel).lower().startswith("r") else self.left_layout
            target.addWidget(plot)
            for t, val in zip(x, y):
                summary.setdefault(t, []).append(val)

        times = sorted(summary.keys())
        min_vals, max_vals, avg_vals = [], [], []
        for t in times:
            vals = summary[t]
            min_vals.append(min(vals))
            max_vals.append(max(vals))
            avg_vals.append(sum(vals) / len(vals))

        self.summary_plot.plot(times, min_vals, pen=pg.mkPen("#E06C75", width=2), name="Min")
        self.summary_plot.plot(times, max_vals, pen=pg.mkPen("#61AFEF", width=2), name="Max")
        self.summary_plot.plot(times, avg_vals, pen=pg.mkPen("#98C379", width=2), name="Avg")

