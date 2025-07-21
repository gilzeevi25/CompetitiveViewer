import sys
from PyQt5.QtWidgets import QApplication, QDialog

from ui.launch_dialog import LaunchDialog
from ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    dialog = LaunchDialog()
    if dialog.exec_() != QDialog.Accepted:
        sys.exit(0)

    window = MainWindow()
    if getattr(dialog, "mep_df", None) is not None:
        window.load_data(
            dialog.mep_df,
            dialog.ssep_upper_df,
            dialog.ssep_lower_df,
            dialog.surgery_meta_df,
        )
        data_dict = {
            "mep_df": dialog.mep_df,
            "ssep_upper_df": dialog.ssep_upper_df,
            "ssep_lower_df": dialog.ssep_lower_df,
        }
        window.trend_tab.refresh(data_dict)
        window.stats_tab.refresh(data_dict)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
