import matplotlib.pyplot as plt


def apply_dark_theme() -> None:
    """Apply a simple dark theme using matplotlib."""
    try:
        plt.style.use("dark_background")
    except Exception:
        pass
