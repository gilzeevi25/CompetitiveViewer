import pyqtgraph as pg
from PyQt5.QtWidgets import QToolTip
from PyQt5.QtGui import QCursor
from .plot_widgets import MEP_PEN, BASELINE_PEN, CustomPlotMenu


class MepView(pg.PlotWidget):
    """Widget for displaying MEP signals."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.showGrid(x=True, y=True, alpha=0.3)
        self.addLegend(offset=(30, 10))
        self.scene().contextMenu = CustomPlotMenu(self)
        self.scene().sigMouseMoved.connect(self._on_hover)

    def _on_hover(self, pos):
        point = self.plotItem.vb.mapSceneToView(pos)
        QToolTip.showText(QCursor.pos(), f"t={point.x():.2f}s\nµV={point.y():.2f}")

    def update_view(self, mep_df, surgery_id, timestamp, channels_ordered):
        """Update the plot with MEP and baseline signals.

        Parameters
        ----------
        mep_df : pandas.DataFrame
            DataFrame containing MEP data.
        surgery_id : any
            Selected surgery id.
        timestamp : any
            Timestamp to display.
        channels_ordered : list
            Channels in the order they should be stacked.
        """
        # Clear previous content
        self.clear()

        if mep_df is None or mep_df.empty:
            return

        subset = mep_df[(mep_df["surgery_id"] == surgery_id) &
                        (mep_df["timestamp"] == timestamp) &
                        (mep_df["channel"].isin(channels_ordered))]
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

        for idx, channel in enumerate(channels_ordered):
            row = subset[subset["channel"] == channel]
            if row.empty:
                continue
            row = row.iloc[0]
            values = row["values"]
            baseline = row["baseline_values"]

            x_values = [i / row["signal_rate"] for i in range(len(values))]
            x_baseline = [i / row["baseline_signal_rate"] for i in range(len(baseline))]
            y_offset = idx * offset_step

            self.plot(
                x_values,
                [v + y_offset for v in values],
                pen=MEP_PEN,
                name=str(channel),
            )
            self.plot(
                x_baseline,
                [v + y_offset for v in baseline],
                pen=BASELINE_PEN,
            )

            text = pg.TextItem(f"{channel} ({row['signal_rate']}Hz)")
            text.setPos(x_values[-1] if x_values else 0, y_offset)
            self.addItem(text)


