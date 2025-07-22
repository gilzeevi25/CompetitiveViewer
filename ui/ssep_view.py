import pandas as pd
import pyqtgraph as pg
from PyQt5.QtWidgets import QWidget, QHBoxLayout

from .plot_widgets import BasePlotWidget, SSEP_U_PEN, SSEP_L_PEN, BASELINE_PEN


class SsepView(QWidget):
    """Widget for displaying SSEP signals with left/right separation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.left_plot = BasePlotWidget()
        self.right_plot = BasePlotWidget()
        layout.addWidget(self.left_plot)
        layout.addWidget(self.right_plot)

    def update_view(self, ssep_upper_df, ssep_lower_df, surgery_id, timestamp, channels_ordered):
        """Update the plots with SSEP and baseline signals."""
        self.left_plot.clear()
        self.right_plot.clear()

        frames = []
        if ssep_upper_df is not None and not ssep_upper_df.empty:
            frames.append(ssep_upper_df.assign(region="Upper"))
        if ssep_lower_df is not None and not ssep_lower_df.empty:
            frames.append(ssep_lower_df.assign(region="Lower"))
        if not frames:
            return

        ssep_df = pd.concat(frames, ignore_index=True)

        subset = ssep_df[
            (ssep_df["surgery_id"] == surgery_id)
            & (ssep_df["timestamp"] == timestamp)
            & (ssep_df["channel"].isin(channels_ordered))
        ]
        if subset.empty:
            return

        def max_abs(seq):
            return max((abs(x) for x in seq), default=0)

        all_max = max(
            max((max_abs(v) for v in subset["values"]), default=1),
            max((max_abs(b) for b in subset["baseline_values"]), default=1),
        )
        offset_step = all_max * 1.2

        # Split rows into left and right groups while preserving channel order
        left_rows = []
        right_rows = []
        for region in ("Lower", "Upper"):
            for ch in channels_ordered:
                rows = subset[(subset["channel"] == ch) & (subset["region"] == region)]
                for _, row in rows.iterrows():
                    target = right_rows if str(ch).lower().startswith("r") else left_rows
                    target.append(row)

        legend_added_left = set()
        legend_added_right = set()

        def plot_group(rows, plot, legend_added):
            for idx, row in enumerate(rows):
                region = row.get("region", "")
                channel = row["channel"]
                values = row["values"]
                baseline = row["baseline_values"]

                x_values = [i / row["signal_rate"] for i in range(len(values))]
                x_baseline = [i / row["baseline_signal_rate"] for i in range(len(baseline))]
                y_offset = idx * offset_step

                pen = SSEP_U_PEN if region == "Upper" else SSEP_L_PEN
                name = region if region not in legend_added else None

                plot.plot(x_values, [v + y_offset for v in values], pen=pen, name=name)
                plot.plot(x_baseline, [v + y_offset for v in baseline], pen=BASELINE_PEN)

                label = f"{region}: {channel}"
                text = pg.TextItem(f"{label} ({row['signal_rate']}Hz)")
                text.setPos(x_values[-1] if x_values else 0, y_offset)
                plot.addItem(text)

                if name:
                    legend_added.add(region)

        plot_group(left_rows, self.left_plot, legend_added_left)
        plot_group(right_rows, self.right_plot, legend_added_right)
