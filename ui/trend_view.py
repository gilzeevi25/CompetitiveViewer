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

        # Plot widget
        self.plot = pg.PlotWidget()
        self.plot.showGrid(x=True, y=True, alpha=0.3)
        layout.addWidget(self.plot)

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
        self.plot.clear()
        if df is None or df.empty:
            self.min_label.setText("Min: N/A")
            self.max_label.setText("Max: N/A")
            self.mean_label.setText("Mean: N/A")
            return

        p2p_df = calculate_p2p(df)

        # Compute stats
        global_min = p2p_df["p2p"].min()
        global_max = p2p_df["p2p"].max()
        global_mean = p2p_df["p2p"].mean()
        self.min_label.setText(f"Min: {global_min:.2f}")
        self.max_label.setText(f"Max: {global_max:.2f}")
        self.mean_label.setText(f"Mean: {global_mean:.2f}")

        for channel in sorted(p2p_df["channel"].unique()):
            subset = p2p_df[p2p_df["channel"] == channel]
            x = subset["timestamp"].to_list()
            y = subset["p2p"].to_list()
            self.plot.plot(x, y, pen=pg.mkPen(width=2), name=str(channel))

