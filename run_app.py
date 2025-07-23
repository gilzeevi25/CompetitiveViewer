"""Entry point for the Tkinter based viewer."""

from tkui.launch_dialog import LaunchDialog
from tkui.main_window import MainWindow


def main() -> None:
    window = MainWindow()
    dialog = LaunchDialog(window)
    dialog.select_file()

    if getattr(dialog, "mep_df", None) is not None:
        window.load_data(
            dialog.mep_df,
            dialog.ssep_upper_df,
            dialog.ssep_lower_df,
            dialog.surgery_meta_df,
        )
    window.show()


if __name__ == "__main__":
    main()
