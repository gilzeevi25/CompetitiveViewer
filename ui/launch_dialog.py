import sys
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, QFileDialog
)

from src import data_loader


class LaunchDialog(QDialog):
    """Modal dialog prompting the user to select a pickle file."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Data File")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Choose a .pkl file to load"))
        open_btn = QPushButton("Open")
        open_btn.clicked.connect(self.select_file)
        layout.addWidget(open_btn)

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Data File",
            "",
            "Pickle Files (*.pkl)"
        )
        if not path:
            sys.exit(0)
        (
            self.mep_df,
            self.ssep_upper_df,
            self.ssep_lower_df,
            self.surgery_meta_df,
        ) = data_loader.load_signals(path)
        self.accept()

