"""Tkinter based UI components for CompetitiveViewer."""

from .main_window import MainWindow
from .launch_dialog import LaunchDialog
from .trend_view import calculate_l1_norm

__all__ = ["MainWindow", "LaunchDialog", "calculate_l1_norm"]
