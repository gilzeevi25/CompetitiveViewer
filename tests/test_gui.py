from PyQt5.QtWidgets import QFileDialog
from ui.launch_dialog import LaunchDialog
from ui.main_window import MainWindow


def test_gui_smoke(qtbot, tiny_pickle, monkeypatch):
    dialog = LaunchDialog()
    qtbot.addWidget(dialog)

    monkeypatch.setattr(QFileDialog, "getOpenFileName", lambda *a, **k: (tiny_pickle, ""))
    dialog.select_file()

    window = MainWindow()
    qtbot.addWidget(window)
    window.load_data(dialog.mep_df, dialog.ssep_upper_df, dialog.ssep_lower_df, dialog.surgery_meta_df)
    window.show()
    qtbot.wait(100)
    assert window.isVisible()
