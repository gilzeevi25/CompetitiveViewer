from tkinter import filedialog

from tkui.launch_dialog import LaunchDialog
from tkui.main_window import MainWindow


def test_gui_smoke(tiny_pickle, monkeypatch):
    window = MainWindow()
    dialog = LaunchDialog(window)
    monkeypatch.setattr(filedialog, "askopenfilename", lambda *a, **k: tiny_pickle)
    dialog.select_file()
    window.load_data(
        dialog.mep_df,
        dialog.ssep_upper_df,
        dialog.ssep_lower_df,
        dialog.surgery_meta_df,
    )
    window.update()
    assert window.mep_df is not None
    window.destroy()
