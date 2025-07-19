from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QAbstractItemView,
    QSlider,
    QSpinBox,
    QPushButton,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt, pyqtSignal


class ChannelListWidget(QListWidget):
    """List widget that emits a signal after internal drag-drop."""

    dropped = pyqtSignal()

    def dropEvent(self, event):
        super().dropEvent(event)
        self.dropped.emit()


class ControlsDock(QWidget):
    """Container widget for controls shown in the dock."""

    channelsReordered = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)

        self.surgery_combo = QComboBox()
        layout.addWidget(self.surgery_combo)

        meta_form = QFormLayout()
        self.date_label = QLabel("N/A")
        self.protocol_label = QLabel("N/A")
        meta_form.addRow("Date:", self.date_label)
        meta_form.addRow("Protocol:", self.protocol_label)
        layout.addLayout(meta_form)

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

        btn_layout = QHBoxLayout()
        self.export_png_btn = QPushButton("Export PNG")
        self.export_csv_btn = QPushButton("Export CSV")
        btn_layout.addWidget(self.export_png_btn)
        btn_layout.addWidget(self.export_csv_btn)
        layout.addLayout(btn_layout)

        layout.addStretch()

        self.channel_list.itemChanged.connect(self._emit_order)
        self.channel_list.dropped.connect(self._emit_order)

    # -----------------------------------------------------
    # Convenience helpers
    # -----------------------------------------------------
    def populate_channels(self, channels, auto_check=True):
        self.channel_list.clear()
        for ch in channels:
            item = QListWidgetItem(str(ch))
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if auto_check else Qt.Unchecked)
            self.channel_list.addItem(item)
        self._emit_order()

    def _emit_order(self):
        order = [self.channel_list.item(i).text() for i in range(self.channel_list.count())]
        self.channelsReordered.emit(order)

