import tkinter as tk
from tkinter import ttk


class MainWindow:
    """Simplified main window implemented with Tkinter."""

    def __init__(self):
        try:
            self.root = tk.Tk()
        except tk.TclError:
            # headless environment
            self.root = tk.Tcl()
        if hasattr(self.root, "title"):
            self.root.title("Competitive Viewer")
        self.label = ttk.Label(self.root, text="No data loaded")
        if hasattr(self.label, "pack"):
            self.label.pack(fill="both", expand=True)

    def load_data(
        self,
        mep_df=None,
        ssep_upper_df=None,
        ssep_lower_df=None,
        surgery_meta_df=None,
    ) -> None:
        """Store loaded data and update label."""
        self.mep_df = mep_df
        self.ssep_upper_df = ssep_upper_df
        self.ssep_lower_df = ssep_lower_df
        self.surgery_meta_df = surgery_meta_df
        if hasattr(self.label, "config"):
            count = len(mep_df) if mep_df is not None else 0
            self.label.config(text=f"MEP rows: {count}")

    def show(self) -> None:
        if hasattr(self.root, "deiconify"):
            self.root.deiconify()

    def isVisible(self) -> bool:
        try:
            return bool(self.root.winfo_exists())
        except Exception:
            return False
