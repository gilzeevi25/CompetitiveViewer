import pyqtgraph as pg


def apply_dark_theme(app):
    """Apply dark stylesheet and pyqtgraph configuration."""
    try:
        with open("resources/dark.qss") as f:
            app.setStyleSheet(f.read())
    except FileNotFoundError:
        pass

    pg.setConfigOptions(
        background="#282C34",
        foreground="#ABB2BF",
        antialias=True,
    )
