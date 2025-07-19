import pandas as pd
import pyqtgraph as pg
from .plot_widgets import (
    BasePlotWidget,
    SSEP_U_PEN,
    SSEP_L_PEN,
    BASELINE_PEN,
)


class SsepView(BasePlotWidget):
    """Widget for displaying SSEP signals."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._legend = self.addLegend(offset=(10, 10))

    def update_view(self, ssep_upper_df, ssep_lower_df, mep_df, surgery_id, timestamp, channels_ordered):
        """Update the plot with SSEP and baseline signals.

        Parameters
        ----------
        ssep_upper_df : pandas.DataFrame
            DataFrame containing upper extremity SSEP data.
        ssep_lower_df : pandas.DataFrame
            DataFrame containing lower extremity SSEP data.
        surgery_id : any
            Selected surgery id.
        timestamp : any
            Timestamp to display.
        channels_ordered : list
            Channels in the order they should be stacked.
        """
        # Clear previous content and legend entries
        self.clear()
        if self._legend is not None:
            self._legend.clear()

        frames = []
        if ssep_upper_df is not None and not ssep_upper_df.empty:
            frames.append(ssep_upper_df.assign(region="Upper"))
            upper_channels = set(ssep_upper_df["channel"].unique())
        else:
            upper_channels = set()
        if ssep_lower_df is not None and not ssep_lower_df.empty:
            frames.append(ssep_lower_df.assign(region="Lower"))
            lower_channels = set(ssep_lower_df["channel"].unique())
        else:
            lower_channels = set()
        if not frames:
            return

        ssep_df = pd.concat(frames, ignore_index=True)

        subset = ssep_df[(ssep_df["surgery_id"] == surgery_id) &
                         (ssep_df["timestamp"] == timestamp) &
                         (ssep_df["channel"].isin(channels_ordered))]
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

        legend_added = set()

        ordered = [ch for ch in channels_ordered if ch in upper_channels] + [ch for ch in channels_ordered if ch in lower_channels]

        for idx, channel in enumerate(ordered):
            row = subset[subset["channel"] == channel]
            if row.empty:
                continue
            row = row.iloc[0]
            values = row["values"]
            baseline = row.get("baseline_values")
            if (baseline is None or len(baseline) == 0) and mep_df is not None:
                mrow = mep_df[(mep_df["surgery_id"] == surgery_id) & (mep_df["channel"] == channel)]
                if not mrow.empty:
                    mrow = mrow.iloc[0]
                    baseline = mrow.get("baseline_values", [])
                else:
                    baseline = []
            region = row.get("region", "")

            x_values = list(range(len(values)))
            x_baseline = list(range(len(baseline)))
            y_offset = idx * offset_step

            pen = SSEP_U_PEN if region == "Upper" else SSEP_L_PEN
            name = region if region not in legend_added else None

            self.plot(
                x_values,
                [v + y_offset for v in values],
                pen=pen,
                name=name,
            )
            self.plot(
                x_baseline,
                [v + y_offset for v in baseline],
                pen=BASELINE_PEN,
            )

            text = pg.TextItem(f"{channel} ({row['signal_rate']}Hz)")
            text.setPos(x_values[-1] if x_values else 0, y_offset)
            self.addItem(text)

            if name:
                legend_added.add(region)
