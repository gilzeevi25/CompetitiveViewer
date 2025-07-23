import tkinter as tk
from tkinter import filedialog, messagebox
from src import data_loader


class LaunchDialog:
    """Simple dialog for selecting a pickle file using Tkinter."""

    def __init__(self, parent=None):
        self.parent = parent
        self.mep_df = None
        self.ssep_upper_df = None
        self.ssep_lower_df = None
        self.surgery_meta_df = None

    def select_file(self):
        path = filedialog.askopenfilename(
            parent=self.parent,
            title="Select Data File",
            filetypes=[("Pickle Files", "*.pkl")],
        )
        if not path:
            return
        try:
            (
                self.mep_df,
                self.ssep_upper_df,
                self.ssep_lower_df,
                self.surgery_meta_df,
            ) = data_loader.load_signals(path)
        except (FileNotFoundError, KeyError) as e:
            messagebox.showerror("Error Loading File", str(e), parent=self.parent)
            return
        return path
