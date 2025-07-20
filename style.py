import os
import sys
from PyQt5.QtWidgets import QApplication
import pyqtgraph as pg


def apply_dark_theme(app: QApplication) -> None:
    """Load dark stylesheet and configure pyqtgraph colors."""
    # When bundled with PyInstaller, resources are extracted to ``sys._MEIPASS``.
    base_dir = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
    qss_path = os.path.join(base_dir, "resources", "dark.qss")
    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        # Fallback to no stylesheet if missing
        pass

    pg.setConfigOptions(
        background="#282C34",
        foreground="#ABB2BF",
        antialias=True,
    )
