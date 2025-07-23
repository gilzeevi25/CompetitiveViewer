import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import pandas as pd

class MainWindow:
    """Simple Tkinter main window showing basic plots."""

    def __init__(self, parent=None):
        self.root = parent or tk.Tk()
        self.root.title("Competitive Viewer")
        self.mep_df = None
        self.ssep_upper_df = None
        self.ssep_lower_df = None
        self.surgery_meta_df = None
        self._setup_ui()

    def _setup_ui(self):
        self.surgery_var = tk.StringVar()
        self.surgery_menu = ttk.Combobox(self.root, textvariable=self.surgery_var)
        self.surgery_menu.pack(fill="x")

        self.channel_list = tk.Listbox(self.root, selectmode=tk.MULTIPLE)
        self.channel_list.pack(fill="both", expand=True)

        self.figure = plt.Figure(figsize=(5, 4))
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.root)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def populate_surgeries(self, surgery_ids):
        self.surgery_menu["values"] = list(surgery_ids)
        if surgery_ids:
            self.surgery_menu.current(0)

    def populate_channels(self, channels):
        self.channel_list.delete(0, tk.END)
        for ch in channels:
            self.channel_list.insert(tk.END, ch)
            self.channel_list.select_set(tk.END)

    def load_data(self, mep_df=None, ssep_upper_df=None, ssep_lower_df=None, surgery_meta_df=None):
        self.mep_df = mep_df
        self.ssep_upper_df = ssep_upper_df
        self.ssep_lower_df = ssep_lower_df
        self.surgery_meta_df = surgery_meta_df

        surgeries = set()
        for df in (mep_df, ssep_upper_df, ssep_lower_df):
            if df is not None:
                surgeries.update(df["surgery_id"].unique())
        self.populate_surgeries(sorted(surgeries))

        df = self._current_dataframe()
        channels = sorted(df["channel"].unique()) if df is not None else []
        self.populate_channels(channels)
        self.update_plots()

    def _current_dataframe(self):
        # only MEP for simplicity
        return self.mep_df

    def update_plots(self):
        self.ax.clear()
        df = self._current_dataframe()
        if df is None or df.empty:
            self.canvas.draw()
            return
        surgery = self.surgery_var.get()
        subset = df[df["surgery_id"] == surgery]
        if subset.empty:
            self.canvas.draw()
            return
        timestamp = subset["timestamp"].iloc[0]
        row = subset.iloc[0]
        values = row["values"]
        x = [i / row["signal_rate"] for i in range(len(values))]
        self.ax.plot(x, values)
        self.ax.set_title(f"{surgery} t={timestamp}")
        self.canvas.draw()

    def show(self):
        self.root.deiconify()

    def run(self):
        self.show()
        self.root.mainloop()
