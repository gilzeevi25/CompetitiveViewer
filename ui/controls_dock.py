from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QDockWidget,
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QLabel,
    QComboBox,
    QListWidget,
    QAbstractItemView,
    QSlider,
    QLineEdit,
    QPushButton,
    QHBoxLayout,
)


class ChannelListWidget(QListWidget):
    """List widget that emits a signal after internal drag-drop."""

    dropped = pyqtSignal()

    def dropEvent(self, event):
        super().dropEvent(event)
        self.dropped.emit()


class ControlsDock(QDockWidget):
    """Dock widget containing all interaction controls."""

    def __init__(self, parent=None):
        super().__init__("Controls", parent)
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.setFeatures(QDockWidget.DockWidgetClosable)
        self.setFixedWidth(280)

        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)

        # Surgery selector
        self.surgery_combo = QComboBox()
        layout.addWidget(self.surgery_combo)

        # Metadata form
        form = QFormLayout()
        self.date_label = QLabel("N/A")
        self.protocol_label = QLabel("N/A")
        form.addRow("Date", self.date_label)
        form.addRow("Protocol", self.protocol_label)
        layout.addLayout(form)

        # Channel list
        self.channel_list = ChannelListWidget()
        self.channel_list.setDragDropMode(QAbstractItemView.InternalMove)
        layout.addWidget(self.channel_list)

        # Timestamp slider and readout
        self.timestamp_slider = QSlider(Qt.Horizontal)
        self.timestamp_slider.setTracking(False)
        layout.addWidget(self.timestamp_slider)
        self.timestamp_label = QLabel("0")
        layout.addWidget(self.timestamp_label)

        # Jump-to-timestamp entry
        goto_layout = QHBoxLayout()
        self.goto_edit = QLineEdit()
        self.goto_edit.setPlaceholderText("Jump to timestamp")
        self.goto_button = QPushButton("Go")
        goto_layout.addWidget(self.goto_edit)
        goto_layout.addWidget(self.goto_button)
        layout.addLayout(goto_layout)

        # Playback controls
        play_layout = QHBoxLayout()
        self.play_button = QPushButton("Play")
        self.pause_button = QPushButton("Pause")
        self.speed_combo = QComboBox()
        self.speed_combo.addItems([
            "x0.5",
            "x0.75",
            "x1",
            "x1.5",
            "x1.75",
            "x2",
            "x5",
        ])
        self.speed_combo.setCurrentText("x1")
        play_layout.addWidget(self.play_button)
        play_layout.addWidget(self.pause_button)
        play_layout.addWidget(self.speed_combo)
        layout.addLayout(play_layout)

        # Export buttons
        export_layout = QHBoxLayout()
        self.export_png_btn = QPushButton("Export PNG")
        self.export_csv_btn = QPushButton("Export CSV")
        export_layout.addWidget(self.export_png_btn)
        export_layout.addWidget(self.export_csv_btn)
        layout.addLayout(export_layout)

        self.setWidget(container)
