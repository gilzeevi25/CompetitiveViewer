import tkinter as tk
from tkinter import filedialog, messagebox

from src import data_loader


class LaunchDialog:
    """Simple dialog for selecting a pickle file using Tkinter."""

    def __init__(self):
        self.mep_df = None
        self.ssep_upper_df = None
        self.ssep_lower_df = None
        self.surgery_meta_df = None

    def select_file(self, path: str | None = None) -> bool:
        """Load the provided file or open a dialog to choose one."""
        if not path:
            try:
                root = tk.Tk()
                root.withdraw()
                path = filedialog.askopenfilename(
                    title="Select Data File",
                    filetypes=[("Pickle Files", "*.pkl")],
                )
                root.destroy()
            except tk.TclError:
                return False
        if not path:
            return False
        try:
            (
                self.mep_df,
                self.ssep_upper_df,
                self.ssep_lower_df,
                self.surgery_meta_df,
            ) = data_loader.load_signals(path)
            return True
        except (FileNotFoundError, KeyError) as e:
            try:
                root = tk.Tk()
                root.withdraw()
                messagebox.showerror("Error Loading File", str(e))
                root.destroy()
            except tk.TclError:
                pass
            return False

    # Compatibility shim for old API
    def exec_(self) -> int:
        return int(self.select_file())
