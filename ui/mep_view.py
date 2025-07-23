import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QHBoxLayout

from .plot_widgets import BasePlotWidget, MEP_PEN, BASELINE_PEN


class MepView(QWidget):
    """Widget for displaying MEP signals with left/right separation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.left_plot = BasePlotWidget()
        self.right_plot = BasePlotWidget()
        layout.addWidget(self.left_plot)
        layout.addWidget(self.right_plot)

    def update_view(self, mep_df, surgery_id, timestamp, channels_ordered):
        """Update the plots with MEP and baseline signals."""
        self.left_plot.clear()
        self.right_plot.clear()

        if mep_df is None or mep_df.empty:
            return

        subset = mep_df[
            (mep_df["surgery_id"] == surgery_id)
            & (mep_df["timestamp"] == timestamp)
            & (mep_df["channel"].isin(channels_ordered))
        ]
        if subset.empty:
            return

        def max_abs(seq):
            return max((abs(x) for x in seq), default=0)

        # Determine offset so traces don't overlap
        all_max = max(
            max((max_abs(v) for v in subset["values"]), default=1),
            max((max_abs(b) for b in subset["baseline_values"]), default=1),
        )
        offset_step = all_max * 1.2

        left_channels = []
        right_channels = []
        for ch in channels_ordered:
            if str(ch).lower().startswith("r"):
                right_channels.append(ch)
            else:
                left_channels.append(ch)

        for idx, channel in enumerate(left_channels):
            row = subset[subset["channel"] == channel]
            if row.empty:
                continue
            row = row.iloc[0]
            values = row["values"]
            baseline = row["baseline_values"]

            x_values = [i / row["signal_rate"] for i in range(len(values))]
            baseline_sr = row.get("baseline_signal_rate", row["signal_rate"])
            x_baseline = [i / baseline_sr for i in range(len(baseline))]
            y_offset = idx * offset_step

            self.left_plot.plot(x_values, [v + y_offset for v in values], pen=MEP_PEN)
            self.left_plot.plot(x_baseline, [v + y_offset for v in baseline], pen=BASELINE_PEN)
            text = pg.TextItem(f"{channel} ({row['signal_rate']}Hz)")
            text.setPos(x_values[-1] if x_values else 0, y_offset)
            self.left_plot.addItem(text)

        for idx, channel in enumerate(right_channels):
            row = subset[subset["channel"] == channel]
            if row.empty:
                continue
            row = row.iloc[0]
            values = row["values"]
            baseline = row["baseline_values"]

            x_values = [i / row["signal_rate"] for i in range(len(values))]
            baseline_sr = row.get("baseline_signal_rate", row["signal_rate"])
            x_baseline = [i / baseline_sr for i in range(len(baseline))]
            y_offset = idx * offset_step

            self.right_plot.plot(x_values, [v + y_offset for v in values], pen=MEP_PEN)
            self.right_plot.plot(x_baseline, [v + y_offset for v in baseline], pen=BASELINE_PEN)
            text = pg.TextItem(f"{channel} ({row['signal_rate']}Hz)")
            text.setPos(x_values[-1] if x_values else 0, y_offset)
            self.right_plot.addItem(text)
