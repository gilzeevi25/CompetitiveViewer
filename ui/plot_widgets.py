from PyQt5.QtWidgets import QMenu, QAction, QFileDialog, QApplication
from pyqtgraph.exporters import ImageExporter
import pyqtgraph as pg
from PyQt5.QtCore import Qt

MEP_PEN = pg.mkPen("#E06C75", width=1.2)
BASELINE_PEN = pg.mkPen("#ABB2BF", width=1, style=pg.QtCore.Qt.DashLine)
SSEP_L_PEN = pg.mkPen("#98C379", width=1.2)
SSEP_U_PEN = pg.mkPen("#61AFEF", width=1.2)


class CustomPlotMenu(QMenu):
    """Context menu for plot widgets."""

    def __init__(self, plot_widget):
        super().__init__(plot_widget)
        self._plot_widget = plot_widget
        export_png = QAction("Export as PNG", self)
        export_png.triggered.connect(self.export_png)
        copy_csv = QAction("Copy CSV of visible data", self)
        copy_csv.triggered.connect(self.copy_csv)
        self.addAction(export_png)
        self.addAction(copy_csv)

    def export_png(self):
        path, _ = QFileDialog.getSaveFileName(self._plot_widget, "Export PNG", "", "PNG Files (*.png)")
        if path:
            exporter = ImageExporter(self._plot_widget.plotItem)
            exporter.export(path)

    def copy_csv(self):
        curves = self._plot_widget.plotItem.listDataItems()
        rows = []
        for curve in curves:
            x, y = curve.getData()
            rows.extend(f"{a},{b}" for a, b in zip(x, y))
        QApplication.clipboard().setText("\n".join(rows))
