import pandas as pd
import pyqtgraph as pg
from PyQt5 import QtWidgets, QtCore, QtGui

# Pens matching the dark theme
MEP_PEN = pg.mkPen("#E06C75", width=1.2)
SSEP_U_PEN = pg.mkPen("#61AFEF", width=1.2)
SSEP_L_PEN = pg.mkPen("#98C379", width=1.2)
BASELINE_PEN = pg.mkPen("#ABB2BF", width=1, style=QtCore.Qt.DashLine)


class CustomPlotMenu(QtWidgets.QMenu):
    """Context menu with export helpers."""

    def __init__(self, widget):
        super().__init__()
        self._widget = widget
        export_png = self.addAction("Export as PNG")
        export_png.triggered.connect(self._export_png)
        copy_csv = self.addAction("Copy CSV of visible data")
        copy_csv.triggered.connect(self._copy_csv)

    def _export_png(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self._widget, "Save Image", "", "PNG Files (*.png)"
        )
        if path:
            exporter = pg.exporters.ImageExporter(self._widget.plotItem)
            exporter.export(path)

    def _copy_csv(self):
        curves = self._widget.listDataItems()
        if not curves:
            return
        data = {}
        for c in curves:
            x, y = c.getData()
            data.setdefault("x", x)
            data[c.name() or "y"] = y
        df = pd.DataFrame(data)
        QtWidgets.QApplication.clipboard().setText(df.to_csv(index=False))


class SignalPlotWidget(pg.PlotWidget):
    """Base plot widget with legend and hover tooltips."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addLegend(offset=(30, 10))
        self._hover_proxy = pg.SignalProxy(
            self.scene().sigMouseMoved, rateLimit=30, slot=self._show_tooltip
        )
        self.scene().contextMenu = CustomPlotMenu(self)
        self.showGrid(x=True, y=True, alpha=0.3)

    def _show_tooltip(self, event):
        pos = event[0]
        if self.plotItem.sceneBoundingRect().contains(pos):
            point = self.plotItem.vb.mapSceneToView(pos)
            QtWidgets.QToolTip.showText(
                QtGui.QCursor.pos(), f"x={point.x():.2f}\ny={point.y():.2f}"
            )


