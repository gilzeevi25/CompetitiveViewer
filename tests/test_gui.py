from ui.launch_dialog import LaunchDialog
from ui.main_window import MainWindow


def test_gui_smoke(tiny_pickle):
    dialog = LaunchDialog()
    assert dialog.select_file(tiny_pickle)

    window = MainWindow()
    window.load_data(
        dialog.mep_df, dialog.ssep_upper_df, dialog.ssep_lower_df, dialog.surgery_meta_df
    )
    window.show()
    assert window.isVisible()
