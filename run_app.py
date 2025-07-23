import tkinter as tk
from tkui.launch_dialog import LaunchDialog
from tkui.main_window import MainWindow


def main() -> None:
    root = tk.Tk()
    root.withdraw()
    dialog = LaunchDialog(root)
    if not dialog.exec_():
        return

    window = MainWindow()
    if getattr(dialog, "mep_df", None) is not None:
        window.load_data(
            dialog.mep_df,
            dialog.ssep_upper_df,
            dialog.ssep_lower_df,
            dialog.surgery_meta_df,
        )
    window.run()


if __name__ == "__main__":
    main()
