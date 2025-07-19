import csv
import io
from PyQt5.QtWidgets import QMenu, QFileDialog, QToolTip
from PyQt5.QtGui import QGuiApplication, QCursor
from PyQt5.QtCore import Qt
import pyqtgraph as pg


MEP_PEN = pg.mkPen("#E06C75", width=1.2)
SSEP_U_PEN = pg.mkPen("#61AFEF", width=1.2)
SSEP_L_PEN = pg.mkPen("#98C379", width=1.2)
BASELINE_PEN = pg.mkPen("#ABB2BF", width=1, style=pg.QtCore.Qt.DashLine)


class CustomPlotMenu(QMenu):
    """Context menu with export helpers."""

    def __init__(self, plot_widget):
        super().__init__()
        self._plot = plot_widget
        self.addAction("Export as PNG", self.export_png)
        self.addAction("Copy CSV of visible data", self.copy_csv)

    def export_png(self):
        path, _ = QFileDialog.getSaveFileName(self._plot, "Export Plot", "", "PNG Image (*.png)")
        if path:
            exporter = pg.exporters.ImageExporter(self._plot.plotItem)
            exporter.export(path)

    def copy_csv(self):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["x", "y"])
        for item in self._plot.listDataItems():
            x, y = item.getData()
            for xv, yv in zip(x, y):
                writer.writerow([xv, yv])
        QGuiApplication.clipboard().setText(output.getvalue())


class BasePlotWidget(pg.PlotWidget):
    """Common plot widget with dark theme helpers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.showGrid(x=True, y=True, alpha=0.3)
        self.addLegend(offset=(30, 10))
        self.scene().contextMenu = CustomPlotMenu(self)
        self._hover_proxy = pg.SignalProxy(self.scene().sigMouseMoved, rateLimit=60, slot=self._show_tooltip)

    def _show_tooltip(self, event):
        pos = event[0]
        if self.sceneBoundingRect().contains(pos):
            point = self.plotItem.vb.mapSceneToView(pos)
            QToolTip.showText(QCursor.pos(), f"{point.x():.2f}, {point.y():.2f}")
