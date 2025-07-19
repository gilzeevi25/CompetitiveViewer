from pathlib import Path
import pyqtgraph as pg


_QSS_PATH = Path(__file__).resolve().parent / "resources" / "dark.qss"


def apply_dark_theme(app):
    """Apply dark stylesheet and PyQtGraph theme to the given QApplication."""
    if _QSS_PATH.exists():
        with open(_QSS_PATH, "r") as f:
            app.setStyleSheet(f.read())
    pg.setConfigOptions(
        background="#282C34",
        foreground="#ABB2BF",
        antialias=True,
    )
