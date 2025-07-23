import tkinter as tk
from tkui import launch_dialog
from tkui.main_window import MainWindow


def test_gui_smoke(tiny_pickle, monkeypatch):
    root = tk.Tk()
    root.withdraw()
    dialog = launch_dialog.LaunchDialog(root)

    monkeypatch.setattr(launch_dialog.filedialog, "askopenfilename", lambda *a, **k: tiny_pickle)
    dialog.select_file()

    window = MainWindow()
    window.load_data(dialog.mep_df, dialog.ssep_upper_df, dialog.ssep_lower_df, dialog.surgery_meta_df)
    window.show()
    root.update_idletasks()
    assert window.root.winfo_exists()
    window.root.destroy()
    root.destroy()
