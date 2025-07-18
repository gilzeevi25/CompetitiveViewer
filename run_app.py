import sys
from PyQt5.QtWidgets import QApplication

from ui.launch_dialog import LaunchDialog
from ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    dialog = LaunchDialog()
    if dialog.exec_() != dialog.Accepted:
        sys.exit(0)

    window = MainWindow()
    if dialog.mep_df is not None:
        surgeries = sorted(dialog.mep_df["surgery_id"].unique())
        channels = sorted(dialog.mep_df["channel"].unique())
        window.populate_surgeries(surgeries)
        window.populate_channels(channels)
        window.trend_tab.refresh({
            "mep_df": dialog.mep_df,
            "ssep_upper_df": dialog.ssep_upper_df,
            "ssep_lower_df": dialog.ssep_lower_df,
        })
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
