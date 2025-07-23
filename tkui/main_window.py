import tkinter as tk
from tkinter import ttk


class MainWindow(tk.Tk):
    """Minimal Tkinter main window for Competitive Viewer."""

    def __init__(self):
        super().__init__()
        self.title("Competitive Viewer")
        self.mep_df = None
        self.ssep_upper_df = None
        self.ssep_lower_df = None
        self.surgery_meta_df = None

        self.label = ttk.Label(self, text="No data loaded")
        self.label.pack(padx=10, pady=10)

    # API similar to PyQt version
    def load_data(
        self,
        mep_df=None,
        ssep_upper_df=None,
        ssep_lower_df=None,
        surgery_meta_df=None,
    ):
        self.mep_df = mep_df
        self.ssep_upper_df = ssep_upper_df
        self.ssep_lower_df = ssep_lower_df
        self.surgery_meta_df = surgery_meta_df
        self.label.config(text="Data loaded")

    def show(self):
        self.mainloop()
