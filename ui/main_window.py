import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QListWidgetItem,
)
from PyQt5.QtWidgets import QApplication
import style
from .controls_dock import ControlsDock

from .trend_view import TrendView
from .mep_view import MepView
from .ssep_view import SsepView
from PyQt5.QtCore import Qt, pyqtSignal




class MainWindow(QMainWindow):
    """Main application window."""

    channelsReordered = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Competitive Viewer")
        self.mep_df = None
        self.ssep_upper_df = None
        self.ssep_lower_df = None
        self.surgery_meta_df = None
        self._start_idx = 0
        self._end_idx = 0
        self._timestamps = []
        style.apply_dark_theme(QApplication.instance())
        self._setup_ui()

    def _setup_ui(self):
        # Central tab widget with views
        self.tabs = QTabWidget()
        self.mep_view = MepView()
        self.ssep_view = SsepView()
        self.tabs.addTab(self.mep_view, "MEP")
        self.tabs.addTab(self.ssep_view, "SSEP")
        self.trend_tab = TrendView()
        self.tabs.addTab(self.trend_tab, "Trend Analysis")
        self.tabs.currentChanged.connect(self._on_tab_changed)
        self.setCentralWidget(self.tabs)

        # Controls dock
        self.controls = ControlsDock(self)
        self.controls.surgery_combo.currentTextChanged.connect(self.on_surgery_changed)
        self.controls.timestamp_slider.valueChanged.connect(self.on_timestamp_changed)
        self.controls.start_spin.valueChanged.connect(self.on_interval_changed)
        self.controls.end_spin.valueChanged.connect(self.on_interval_changed)
        self.controls.channel_list.itemChanged.connect(self.on_channels_changed)
        self.controls.channel_list.dropped.connect(self._emit_channel_order)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.controls)

        self.channelsReordered.connect(self.trend_tab.set_channel_order)

    def populate_surgeries(self, surgery_ids):
        self.controls.surgery_combo.clear()
        self.controls.surgery_combo.addItems([str(s) for s in surgery_ids])

    def populate_channels(self, channels, auto_check=True):
        self.controls.channel_list.clear()
        for ch in channels:
            item = QListWidgetItem(str(ch))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            if auto_check:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.controls.channel_list.addItem(item)
        # Emit initial order
        self._emit_channel_order()

    # -----------------------------------------------------
    # Data loading
    # -----------------------------------------------------
    def load_data(
        self,
        mep_df=None,
        ssep_upper_df=None,
        ssep_lower_df=None,
        surgery_meta_df=None,
    ):
        """Store dataframes and populate controls."""
        self.mep_df = mep_df
        self.ssep_upper_df = ssep_upper_df
        self.ssep_lower_df = ssep_lower_df
        self.surgery_meta_df = surgery_meta_df

        surgeries = set()
        for df in (mep_df, ssep_upper_df, ssep_lower_df):
            if df is not None:
                surgeries.update(df["surgery_id"].unique())
        self.populate_surgeries(sorted(surgeries))

        self._update_channels_for_current_tab()
        self._update_timestamp_slider()
        self._update_surgery_meta_label()
        self.update_plots()

    def on_surgery_changed(self, value):
        self._update_timestamp_slider()
        self._update_surgery_meta_label()
        self.update_plots()

    def on_timestamp_changed(self, value):
        self.update_plots()

    def on_interval_changed(self, value):
        self._start_idx = min(self.controls.start_spin.value(), self.controls.end_spin.value())
        self._end_idx = max(self.controls.start_spin.value(), self.controls.end_spin.value())
        self.controls.timestamp_slider.setMinimum(self._start_idx)
        self.controls.timestamp_slider.setMaximum(self._end_idx)
        if not (self._start_idx <= self.controls.timestamp_slider.value() <= self._end_idx):
            self.controls.timestamp_slider.setValue(self._start_idx)
        self.update_plots()

    def on_channels_changed(self, item):
        self.update_plots()

    def _emit_channel_order(self):
        order = [self.controls.channel_list.item(i).text() for i in range(self.controls.channel_list.count())]
        self.channelsReordered.emit(order)
        self.update_plots()

    # -----------------------------------------------------
    # Internal helpers
    # -----------------------------------------------------
    def _on_tab_changed(self, index):
        self._update_channels_for_current_tab()
        self._update_timestamp_slider()
        self.update_plots()

    def _current_dataframe(self):
        if self.tabs.currentIndex() == 0:
            return self.mep_df
        frames = []
        if self.ssep_upper_df is not None:
            frames.append(self.ssep_upper_df)
        if self.ssep_lower_df is not None:
            frames.append(self.ssep_lower_df)
        if frames:
            return pd.concat(frames, ignore_index=True)
        return None

    def _update_channels_for_current_tab(self):
        if self.tabs.currentIndex() == 0:
            df = self.mep_df
            channels = sorted(df["channel"].unique()) if df is not None else []
        else:
            channels = set()
            if self.ssep_upper_df is not None:
                channels.update(self.ssep_upper_df["channel"].unique())
            if self.ssep_lower_df is not None:
                channels.update(self.ssep_lower_df["channel"].unique())
            channels = sorted(channels)
        self.populate_channels(channels)

    def _update_timestamp_slider(self):
        df = self._current_dataframe()
        if df is None or df.empty:
            self._timestamps = []
            self.controls.timestamp_slider.setMaximum(0)
            return
        surgery = self.controls.surgery_combo.currentText()
        subset = df[df["surgery_id"] == surgery]
        unique_ts = sorted(subset["timestamp"].unique())
        self._timestamps = unique_ts
        if unique_ts:
            self.controls.timestamp_slider.setMinimum(0)
            self.controls.timestamp_slider.setMaximum(len(unique_ts) - 1)
            self.controls.start_spin.setMaximum(len(unique_ts) - 1)
            self.controls.end_spin.setMaximum(len(unique_ts) - 1)
            self.controls.start_spin.setValue(0)
            self.controls.end_spin.setValue(len(unique_ts) - 1)
            self._start_idx = 0
            self._end_idx = len(unique_ts) - 1
            self.controls.timestamp_slider.setMinimum(self._start_idx)
            self.controls.timestamp_slider.setMaximum(self._end_idx)
            self.controls.timestamp_slider.setValue(self._start_idx)
        else:
            self.controls.timestamp_slider.setMaximum(0)

    def update_plots(self):
        channels = [self.controls.channel_list.item(i).text()
                    for i in range(self.controls.channel_list.count())
                    if self.controls.channel_list.item(i).checkState() == Qt.Checked]
        timestamp = None
        idx = self.controls.timestamp_slider.value()
        if 0 <= idx < len(self._timestamps):
            timestamp = self._timestamps[idx]
        surgery = self.controls.surgery_combo.currentText()

        if self.tabs.currentIndex() == 0:
            self.mep_view.update_view(self.mep_df, surgery, timestamp, channels)
        else:
            self.ssep_view.update_view(
                self.ssep_upper_df,
                self.ssep_lower_df,
                surgery,
                timestamp,
                channels,
            )

    def _update_surgery_meta_label(self):
        if self.surgery_meta_df is None or self.surgery_meta_df.empty:
            self.controls.date_label.setText("N/A")
            self.controls.protocol_label.setText("N/A")
            return
        sid = self.controls.surgery_combo.currentText()
        if sid in self.surgery_meta_df.index:
            row = self.surgery_meta_df.loc[sid]
        elif "surgery_id" in self.surgery_meta_df.columns:
            row = self.surgery_meta_df[self.surgery_meta_df["surgery_id"] == sid]
            row = row.iloc[0] if not row.empty else None
        else:
            row = None
        if row is None:
            self.controls.date_label.setText("N/A")
            self.controls.protocol_label.setText("N/A")
        else:
            date = row.get("date", "N/A")
            protocol = row.get("protocol", "N/A")
            self.controls.date_label.setText(str(date))
            self.controls.protocol_label.setText(str(protocol))


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.populate_surgeries([1, 2, 3])
    window.populate_channels(['ch1', 'ch2', 'ch3'])
    window.show()
    sys.exit(app.exec_())
