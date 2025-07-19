import os
import pyqtgraph as pg


def apply_dark_theme(app):
    """Apply the bundled dark theme to the given QApplication."""
    qss_path = os.path.join(os.path.dirname(__file__), "resources", "dark.qss")
    try:
        with open(qss_path, "r", encoding="utf-8") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass

    pg.setConfigOptions(
        background="#282C34",
        foreground="#ABB2BF",
        antialias=True,
    )
