import sys
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout,
    QDockWidget, QComboBox, QSlider, QListWidget,
    QListWidgetItem
)

from .trend_view import TrendView
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Competitive Viewer")
        self._setup_ui()

    def _setup_ui(self):
        # Central tab widget
        self.tabs = QTabWidget()
        self.tabs.addTab(QWidget(), "MEP")
        self.tabs.addTab(QWidget(), "SSEP")
        self.trend_tab = TrendView()
        self.tabs.addTab(self.trend_tab, "Trend Analysis")
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

        # Timestamp slider
        self.timestamp_slider = QSlider(Qt.Horizontal)
        self.timestamp_slider.setMinimum(0)
        self.timestamp_slider.setMaximum(100)
        self.timestamp_slider.valueChanged.connect(self.on_timestamp_changed)
        dock_layout.addWidget(self.timestamp_slider)

        # Channel selection list
        self.channel_list = QListWidget()
        self.channel_list.itemChanged.connect(self.on_channels_changed)
        dock_layout.addWidget(self.channel_list)

        dock.setWidget(dock_container)

    def populate_surgeries(self, surgery_ids):
        self.surgery_combo.clear()
        self.surgery_combo.addItems([str(s) for s in surgery_ids])

    def populate_channels(self, channels):
        self.channel_list.clear()
        for ch in channels:
            item = QListWidgetItem(str(ch))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.channel_list.addItem(item)

    def on_surgery_changed(self, value):
        print(f"Surgery changed: {value}")

    def on_timestamp_changed(self, value):
        print(f"Timestamp changed: {value}")

    def on_channels_changed(self, item):
        checked_channels = [self.channel_list.item(i).text()
                            for i in range(self.channel_list.count())
                            if self.channel_list.item(i).checkState() == Qt.Checked]
        print(f"Channels changed: {checked_channels}")


if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.populate_surgeries([1, 2, 3])
    window.populate_channels(['ch1', 'ch2', 'ch3'])
    window.show()
    sys.exit(app.exec_())
