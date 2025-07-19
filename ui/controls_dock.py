from PyQt5.QtWidgets import (
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QSlider,
    QSpinBox,
    QHBoxLayout,
    QPushButton,
)
from PyQt5.QtCore import Qt, pyqtSignal


class ChannelListWidget(QListWidget):
    """List widget that emits a signal after internal drag-drop."""

    dropped = pyqtSignal()

    def dropEvent(self, event):
        super().dropEvent(event)
        self.dropped.emit()


class ControlsDock(QDockWidget):
    """Collapsible dock with signal controls."""

    def __init__(self, parent=None):
        super().__init__("Controls", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        container = QWidget()
        layout = QVBoxLayout(container)

        self.surgery_combo = QComboBox()
        layout.addWidget(self.surgery_combo)

        form = QFormLayout()
        self.date_label = QLabel("N/A")
        self.protocol_label = QLabel("N/A")
        form.addRow("Date:", self.date_label)
        form.addRow("Protocol:", self.protocol_label)
        layout.addLayout(form)

        self.channel_list = ChannelListWidget()
        self.channel_list.setDragDropMode(QAbstractItemView.InternalMove)
        layout.addWidget(self.channel_list)

        self.timestamp_slider = QSlider(Qt.Horizontal)
        layout.addWidget(self.timestamp_slider)

        interval_layout = QHBoxLayout()
        self.start_spin = QSpinBox()
        self.end_spin = QSpinBox()
        interval_layout.addWidget(self.start_spin)
        interval_layout.addWidget(self.end_spin)
        layout.addLayout(interval_layout)

        export_layout = QHBoxLayout()
        self.export_png_btn = QPushButton("Export PNG")
        self.export_csv_btn = QPushButton("Export CSV")
        export_layout.addWidget(self.export_png_btn)
        export_layout.addWidget(self.export_csv_btn)
        layout.addLayout(export_layout)

        self.setWidget(container)
        self.setMinimumWidth(280)
        self.setMaximumWidth(280)
