import sys

from ui.launch_dialog import LaunchDialog
from ui.main_window import MainWindow


def main() -> None:
    dialog = LaunchDialog()
    if not dialog.select_file():
        sys.exit(0)

    window = MainWindow()
    if getattr(dialog, "mep_df", None) is not None:
        window.load_data(
            dialog.mep_df,
            dialog.ssep_upper_df,
            dialog.ssep_lower_df,
            dialog.surgery_meta_df,
        )
    window.show()
    if hasattr(window.root, "mainloop"):
        window.root.mainloop()


if __name__ == "__main__":
    main()
