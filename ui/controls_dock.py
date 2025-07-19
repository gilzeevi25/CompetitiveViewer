from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QLabel,
    QListWidget,
    QSlider,
    QSpinBox,
    QPushButton,
    QHBoxLayout,
    QAbstractItemView,
    QListWidgetItem,
)


class ChannelListWidget(QListWidget):
    """List widget emitting a signal after internal drag-drop."""

    dropped = pyqtSignal()

    def dropEvent(self, event):
        super().dropEvent(event)
        self.dropped.emit()


class ControlsDock(QDockWidget):
    """Dock widget containing surgery controls."""

    def __init__(self, parent=None):
        super().__init__("Controls", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setMinimumWidth(280)
        self.setMaximumWidth(280)

        container = QWidget()
        layout = QVBoxLayout(container)

        self.surgery_combo = QComboBox()
        layout.addWidget(self.surgery_combo)

        meta_form = QFormLayout()
        self.date_label = QLabel("N/A")
        self.protocol_label = QLabel("N/A")
        meta_form.addRow("Date", self.date_label)
        meta_form.addRow("Protocol", self.protocol_label)
        layout.addLayout(meta_form)

        self.channel_list = ChannelListWidget()
        self.channel_list.setDragDropMode(QAbstractItemView.InternalMove)
        layout.addWidget(self.channel_list)

        self.timestamp_slider = QSlider(Qt.Horizontal)
        layout.addWidget(self.timestamp_slider)

        interval_form = QFormLayout()
        self.start_spin = QSpinBox()
        self.end_spin = QSpinBox()
        interval_form.addRow("Start", self.start_spin)
        interval_form.addRow("End", self.end_spin)
        layout.addLayout(interval_form)

        btn_layout = QHBoxLayout()
        self.export_png_btn = QPushButton("Export PNG")
        self.export_csv_btn = QPushButton("Copy CSV")
        btn_layout.addWidget(self.export_png_btn)
        btn_layout.addWidget(self.export_csv_btn)
        layout.addLayout(btn_layout)

        self.setWidget(container)

    def populate_channels(self, channels, auto_check=True):
        self.channel_list.clear()
        for ch in channels:
            item = QListWidgetItem(str(ch))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if auto_check else Qt.Unchecked)
            self.channel_list.addItem(item)

