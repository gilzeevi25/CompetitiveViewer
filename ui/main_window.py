import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QApplication,
)

from .controls_dock import ControlsDock
from PyQt5.QtWidgets import QListWidgetItem

from .trend_view import TrendView
from .mep_view import MepView
from .ssep_view import SsepView
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
import style


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
        self._timestamps = []
        self.play_timer = QTimer(self)
        self.play_timer.timeout.connect(self._advance_playback)
        self._play_interval_ms = 1000
        self._setup_ui()

    def _setup_ui(self):
        style.apply_dark_theme(QApplication.instance())
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
        self.addDockWidget(Qt.LeftDockWidgetArea, self.controls)

        self.surgery_combo = self.controls.surgery_combo
        self.controls.surgery_combo.currentTextChanged.connect(self.on_surgery_changed)

        self.timestamp_slider = self.controls.timestamp_slider
        self.timestamp_slider.valueChanged.connect(self.on_timestamp_changed)
        self.timestamp_slider.sliderMoved.connect(self._update_timestamp_label)

        self.timestamp_label = self.controls.timestamp_label
        self.controls.goto_button.clicked.connect(self._goto_timestamp)
        self.controls.goto_edit.returnPressed.connect(self._goto_timestamp)

        self.controls.play_button.clicked.connect(self.start_playback)
        self.controls.pause_button.clicked.connect(self.pause_playback)

        self.channel_list = self.controls.channel_list
        self.channel_list.itemChanged.connect(self.on_channels_changed)
        self.channel_list.dropped.connect(self._emit_channel_order)

        self.channelsReordered.connect(self.trend_tab.set_channel_order)

        self.date_label = self.controls.date_label
        self.protocol_label = self.controls.protocol_label

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


    def on_channels_changed(self, item):
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
        self.play_timer.stop()
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
            self._update_timestamp_label(0)
        else:
            self.timestamp_slider.setMaximum(0)

    def update_plots(self):
        channels = [self.channel_list.item(i).text()
                    for i in range(self.channel_list.count())
                    if self.channel_list.item(i).checkState() == Qt.Checked]
        timestamp = None
        idx = self.timestamp_slider.value()
        if 0 <= idx < len(self._timestamps):
            timestamp = self._timestamps[idx]
        self._update_timestamp_label(idx)
        surgery = self.surgery_combo.currentText()

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
            self.date_label.setText("N/A")
            self.protocol_label.setText("N/A")
            return
        sid = self.surgery_combo.currentText()
        if sid in self.surgery_meta_df.index:
            row = self.surgery_meta_df.loc[sid]
        elif "surgery_id" in self.surgery_meta_df.columns:
            row = self.surgery_meta_df[self.surgery_meta_df["surgery_id"] == sid]
            row = row.iloc[0] if not row.empty else None
        else:
            row = None
        if row is None:
            self.date_label.setText("N/A")
            self.protocol_label.setText("N/A")
        else:
            date = row.get("date", "N/A")
            protocol = row.get("protocol", "N/A")
            self.date_label.setText(str(date))
            self.protocol_label.setText(str(protocol))

    def _update_timestamp_label(self, slider_value):
        """Update label showing the explicit timestamp."""
        if 0 <= slider_value < len(self._timestamps):
            value = self._timestamps[slider_value]
        else:
            value = "N/A"
        self.timestamp_label.setText(str(value))

    def _goto_timestamp(self):
        """Jump slider to the timestamp entered by the user."""
        text = self.controls.goto_edit.text()
        if not text:
            return
        try:
            # attempt numeric comparison first
            target = float(text)
        except ValueError:
            target = text
        if target in self._timestamps:
            idx = self._timestamps.index(target)
            self.timestamp_slider.setValue(idx)
            self._update_timestamp_label(idx)
            self.update_plots()

    # -----------------------------------------------------
    # Playback helpers
    # -----------------------------------------------------
    def start_playback(self):
        """Begin automatic stepping through timestamps."""
        if not self._timestamps:
            return
        speed_text = self.controls.speed_combo.currentText().lstrip("x")
        try:
            speed = float(speed_text)
        except ValueError:
            speed = 1.0
        interval = int(self._play_interval_ms / speed)
        if interval <= 0:
            interval = 1
        self.play_timer.start(interval)

    def pause_playback(self):
        """Pause the playback timer."""
        self.play_timer.stop()

    def _advance_playback(self):
        idx = self.timestamp_slider.value() + 1
        if idx > self.timestamp_slider.maximum():
            self.play_timer.stop()
            return
        self.timestamp_slider.setValue(idx)


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.populate_surgeries([1, 2, 3])
    window.populate_channels(['ch1', 'ch2', 'ch3'])
    window.show()
    sys.exit(app.exec_())
