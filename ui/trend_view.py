import pandas as pd
import numpy as np
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QWidget as QtWidget,
)
import pyqtgraph as pg
from .plot_widgets import BasePlotWidget


def calculate_l1_norm(df: pd.DataFrame) -> pd.DataFrame:
    """Compute L1 norm for each timestamp/channel row."""
    if df is None or df.empty:
        return pd.DataFrame(columns=["timestamp", "channel", "l1"])

    result = df[["timestamp", "channel", "values"]].copy()
    result["l1"] = result["values"].apply(
        lambda arr: float(np.sum(np.abs(arr))) if len(arr) > 0 else 0.0
    )
    return result[["timestamp", "channel", "l1"]]


class TrendView(QWidget):
    """Widget for displaying L1-norm trends across time."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.mep_df = None
        self.ssep_upper_df = None
        self.ssep_lower_df = None
        self._channel_order = []

        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Modality selection
        top = QHBoxLayout()
        top.addWidget(QLabel("Modality:"))
        self.modality_combo = QComboBox()
        self.modality_combo.addItems(["MEP", "SSEP_UPPER", "SSEP_LOWER"])
        self.modality_combo.currentTextChanged.connect(self.update_view)
        top.addWidget(self.modality_combo)
        layout.addLayout(top)

        # Container for channel plots
        self.channel_container = QtWidget()
        channel_layout = QHBoxLayout(self.channel_container)
        self.left_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()
        channel_layout.addLayout(self.left_layout)
        channel_layout.addLayout(self.right_layout)
        layout.addWidget(self.channel_container)

        # Summary plot
        self.summary_plot = BasePlotWidget()
        self._summary_legend = self.summary_plot.plotItem.legend
        layout.addWidget(self.summary_plot)

        self._channel_plots = []

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

    # -----------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------
    def _current_dataframe(self) -> pd.DataFrame:
        modality = self.modality_combo.currentText()
        if modality == "MEP":
            return self.mep_df
        if modality == "SSEP_UPPER":
            return self.ssep_upper_df
        if modality == "SSEP_LOWER":
            return self.ssep_lower_df
        return None

    def update_view(self) -> None:
        df = self._current_dataframe()

        # Clear previous channel plots
        for layout in (self.left_layout, self.right_layout):
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.setParent(None)
        self._channel_plots.clear()

        self.summary_plot.clear()
        if self._summary_legend is not None:
            self._summary_legend.clear()

        if df is None or df.empty:
            return

        l1_df = calculate_l1_norm(df)

        unique_channels = list(l1_df["channel"].unique())
        if self._channel_order:
            channels = [ch for ch in self._channel_order if ch in unique_channels]
            for ch in unique_channels:
                if ch not in channels:
                    channels.append(ch)
        else:
            channels = sorted(unique_channels)

        prefix = ""
        modality = self.modality_combo.currentText()
        if modality == "SSEP_UPPER":
            prefix = "Upper: "
        elif modality == "SSEP_LOWER":
            prefix = "Lower: "

        # Plot per-channel trends
        for idx, channel in enumerate(channels):
            subset = l1_df[l1_df["channel"] == channel]
            if subset.empty:
                continue
            x = subset["timestamp"].to_list()
            y = subset["l1"].to_list()

            plot = BasePlotWidget()
            plot.plot(x, y, pen=pg.mkPen(pg.intColor(idx, hues=len(channels)), width=2))
            plot.setTitle(f"{prefix}{channel}")
            target = self.right_layout if str(channel).lower().startswith("r") else self.left_layout
            target.addWidget(plot)
            self._channel_plots.append(plot)

        # Global summary
        filtered = l1_df[l1_df["channel"].isin(channels)]
        if filtered.empty:
            return
        summary = (
            filtered.groupby("timestamp")["l1"].agg(["min", "max", "mean"]).reset_index()
        )
        self.summary_plot.plot(summary["timestamp"], summary["min"], pen=pg.mkPen("r", width=2), name="Min")
        self.summary_plot.plot(summary["timestamp"], summary["max"], pen=pg.mkPen("g", width=2), name="Max")
        self.summary_plot.plot(summary["timestamp"], summary["mean"], pen=pg.mkPen("b", width=2), name="Avg")

