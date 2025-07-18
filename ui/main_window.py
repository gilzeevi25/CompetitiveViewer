import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QDockWidget,
    QComboBox,
    QSlider,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QLabel,
    QSpinBox,
)

from .trend_view import TrendView
from .mep_view import MepView
from .ssep_view import SsepView
from PyQt5.QtCore import Qt, pyqtSignal


class ChannelListWidget(QListWidget):
    """List widget that emits a signal after internal drag-drop."""

    dropped = pyqtSignal()

    def dropEvent(self, event):
        super().dropEvent(event)
        self.dropped.emit()


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
        self._sample_start = 0
        self._sample_end = 0
        self._timestamps = []
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

        # Dock widget on the left for controls
        dock = QDockWidget("Controls", self)
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        dock_container = QWidget()
        dock_layout = QVBoxLayout(dock_container)

        # Surgery selection
        self.surgery_combo = QComboBox()
        self.surgery_combo.currentTextChanged.connect(self.on_surgery_changed)
        dock_layout.addWidget(self.surgery_combo)

        # Surgery metadata display
        self.surgery_meta_label = QLabel("")
        dock_layout.addWidget(self.surgery_meta_label)

        # Sample interval selection
        self.start_spin = QSpinBox()
        self.end_spin = QSpinBox()
        self.start_spin.setRange(0, 0)
        self.end_spin.setRange(0, 0)
        self.start_spin.setPrefix("Start ")
        self.end_spin.setPrefix("End ")
        self.start_spin.valueChanged.connect(self.on_interval_changed)
        self.end_spin.valueChanged.connect(self.on_interval_changed)
        dock_layout.addWidget(self.start_spin)
        dock_layout.addWidget(self.end_spin)

        # Timestamp slider
        self.timestamp_slider = QSlider(Qt.Horizontal)
        self.timestamp_slider.setMinimum(0)
        self.timestamp_slider.setMaximum(100)
        self.timestamp_slider.valueChanged.connect(self.on_timestamp_changed)
        dock_layout.addWidget(self.timestamp_slider)

        # Channel selection list
        self.channel_list = ChannelListWidget()
        self.channel_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.channel_list.itemChanged.connect(self.on_channels_changed)
        self.channel_list.dropped.connect(self._emit_channel_order)
        dock_layout.addWidget(self.channel_list)

        self.channelsReordered.connect(self.trend_tab.set_channel_order)

        dock.setWidget(dock_container)

    def populate_surgeries(self, surgery_ids):
        self.surgery_combo.clear()
        self.surgery_combo.addItems([str(s) for s in surgery_ids])

    def populate_channels(self, channels, auto_check=True):
        self.channel_list.clear()
        for ch in channels:
            item = QListWidgetItem(str(ch))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            if auto_check:
                item.setCheckState(Qt.Checked)
            else:
                item.setCheckState(Qt.Unchecked)
            self.channel_list.addItem(item)
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
        self._update_surgery_meta_display()

        self._update_channels_for_current_tab()
        self._update_timestamp_slider()
        self.update_plots()

    def on_surgery_changed(self, value):
        self._update_timestamp_slider()
        self._update_surgery_meta_display()
        self.update_plots()

    def on_timestamp_changed(self, value):
        self.update_plots()

    def on_channels_changed(self, item):
        self.update_plots()

    def on_interval_changed(self, value):
        if self.end_spin.value() < self.start_spin.value():
            self.end_spin.setValue(self.start_spin.value())
        self._sample_start = self.start_spin.value()
        self._sample_end = self.end_spin.value()
        self.update_plots()

    def _emit_channel_order(self):
        order = [self.channel_list.item(i).text() for i in range(self.channel_list.count())]
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

    def _update_interval_controls(self, subset: pd.DataFrame) -> None:
        """Update sample range spin boxes based on the current subset."""
        if subset is None or subset.empty:
            self.start_spin.setMinimum(0)
            self.start_spin.setMaximum(0)
            self.end_spin.setMinimum(0)
            self.end_spin.setMaximum(0)
            self.start_spin.setValue(0)
            self.end_spin.setValue(0)
            self._sample_start = 0
            self._sample_end = 0
            return

        max_len = int(subset["values"].apply(len).max())
        self.start_spin.setMinimum(0)
        self.start_spin.setMaximum(max_len - 1)
        self.end_spin.setMinimum(0)
        self.end_spin.setMaximum(max_len - 1)
        if self.end_spin.value() >= max_len:
            self.end_spin.setValue(max_len - 1)
        if self.start_spin.value() >= max_len:
            self.start_spin.setValue(0)
        self._sample_start = self.start_spin.value()
        self._sample_end = self.end_spin.value()

    def _update_surgery_meta_display(self) -> None:
        """Display date and protocol for the currently selected surgery."""
        if self.surgery_meta_df is None or self.surgery_meta_df.empty:
            self.surgery_meta_label.setText("")
            return

        surgery_id = self.surgery_combo.currentText()
        row = self.surgery_meta_df[self.surgery_meta_df.index.astype(str) == str(surgery_id)]
        if row.empty:
            self.surgery_meta_label.setText("")
        else:
            row = row.iloc[0]
            date = row.get("date", "N/A")
            protocol = row.get("protocol", "N/A")
            self.surgery_meta_label.setText(f"Date: {date} | Protocol: {protocol}")

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
            self.timestamp_slider.setMaximum(0)
            return
        surgery = self.surgery_combo.currentText()
        subset = df[df["surgery_id"] == surgery]
        unique_ts = sorted(subset["timestamp"].unique())
        self._timestamps = unique_ts
        if unique_ts:
            self.timestamp_slider.setMinimum(0)
            self.timestamp_slider.setMaximum(len(unique_ts) - 1)
            self.timestamp_slider.setValue(0)
        else:
            self.timestamp_slider.setMaximum(0)

        self._update_interval_controls(subset)

    def update_plots(self):
        channels = [self.channel_list.item(i).text()
                    for i in range(self.channel_list.count())
                    if self.channel_list.item(i).checkState() == Qt.Checked]
        timestamp = None
        idx = self.timestamp_slider.value()
        if 0 <= idx < len(self._timestamps):
            timestamp = self._timestamps[idx]
        surgery = self.surgery_combo.currentText()

        if self.tabs.currentIndex() == 0:
            self.mep_view.update_view(
                self.mep_df,
                surgery,
                timestamp,
                channels,
                self._sample_start,
                self._sample_end,
            )
        else:
            self.ssep_view.update_view(
                self.ssep_upper_df,
                self.ssep_lower_df,
                surgery,
                timestamp,
                channels,
                self._sample_start,
                self._sample_end,
            )


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.populate_surgeries([1, 2, 3])
    window.populate_channels(['ch1', 'ch2', 'ch3'])
    window.show()
    sys.exit(app.exec_())
