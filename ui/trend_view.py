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
    """Compute L1 norm for each timestamp/channel row."""
    if df is None or df.empty:
        return pd.DataFrame(columns=["timestamp", "channel", "l1"])

    result = df[["timestamp", "channel", "values"]].copy()

    def l1(arr):
        return float(sum(abs(x) for x in arr)) if len(arr) > 0 else 0.0

    result["l1"] = result["values"].apply(l1)
    return result[["timestamp", "channel", "l1"]]


class TrendView(QWidget):
    """Widget for displaying L1-norm trends across time."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.mep_df = None
        self.ssep_upper_df = None
        self.ssep_lower_df = None
        self._channel_order = []

        self._plots = []
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Modality selector
        combo_layout = QHBoxLayout()
        combo_layout.addWidget(QLabel("Modality:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["MEP", "SSEP_UPPER", "SSEP_LOWER"])
        self.mode_combo.currentIndexChanged.connect(self.update_view)
        combo_layout.addWidget(self.mode_combo)
        layout.addLayout(combo_layout)

        # Container for channel subplots
        self._left_layout = QVBoxLayout()
        self._right_layout = QVBoxLayout()
        columns = QHBoxLayout()
        columns.addLayout(self._left_layout)
        columns.addLayout(self._right_layout)
        layout.addLayout(columns)

        # Global summary plot
        self.summary_plot = BasePlotWidget()
        self._summary_legend = self.summary_plot.plotItem.legend
        layout.addWidget(self.summary_plot)

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
        mode = self.mode_combo.currentText()
        if mode == "MEP":
            return self.mep_df
        if mode == "SSEP_UPPER":
            return self.ssep_upper_df
        if mode == "SSEP_LOWER":
            return self.ssep_lower_df
        return None

    def update_view(self) -> None:
        df = self._current_dataframe()

        # Clear previous plots
        for layout in (self._left_layout, self._right_layout):
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().setParent(None)
        self._plots = []

        self.summary_plot.clear()
        if self._summary_legend is not None:
            self._summary_legend.clear()

        if df is None or df.empty:
            return

        l1_df = calculate_l1(df)

        unique_channels = list(l1_df["channel"].unique())
        if self._channel_order:
            channels = [ch for ch in self._channel_order if ch in unique_channels]
            for ch in unique_channels:
                if ch not in channels:
                    channels.append(ch)
        else:
            channels = sorted(unique_channels)

        mode = self.mode_combo.currentText()

        for idx, channel in enumerate(channels):
            subset = l1_df[l1_df["channel"] == channel]
            x = subset["timestamp"].to_list()
            y = subset["l1"].to_list()
            color = pg.intColor(idx, hues=len(channels))
            plot = BasePlotWidget()
            plot.plot(x, y, pen=pg.mkPen(color, width=2))
            plot.setLabel("bottom", "Time (s)")
            plot.setLabel("left", "L1 Norm")
            title = str(channel)
            if mode == "SSEP_UPPER":
                title = f"Upper: {title}"
            elif mode == "SSEP_LOWER":
                title = f"Lower: {title}"
            plot.setTitle(title)
            target_layout = (
                self._right_layout
                if str(channel).lower().startswith("r")
                else self._left_layout
            )
            target_layout.addWidget(plot)
            self._plots.append(plot)

        summary = (
            l1_df.groupby("timestamp")["l1"].agg(["min", "max", "mean"]).reset_index()
        )

        pens = {
            "min": pg.mkPen("#61AFEF", width=2),
            "max": pg.mkPen("#E06C75", width=2),
            "mean": pg.mkPen("#98C379", width=2),
        }

        for name in ("min", "max", "mean"):
            self.summary_plot.plot(
                summary["timestamp"].to_list(),
                summary[name].to_list(),
                pen=pens[name],
                name=name.capitalize(),
            )
        self.summary_plot.setLabel("bottom", "Time (s)")
        self.summary_plot.setLabel("left", "L1 Norm")

