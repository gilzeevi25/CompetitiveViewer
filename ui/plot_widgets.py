import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets

# Predefined pens matching the dark theme
MEP_PEN = pg.mkPen("#E06C75", width=1.2)
SSEP_U_PEN = pg.mkPen("#61AFEF", width=1.2)
SSEP_L_PEN = pg.mkPen("#98C379", width=1.2)
BASELINE_PEN = pg.mkPen("#ABB2BF", width=1, style=QtCore.Qt.DashLine)


class CustomPlotMenu(QtWidgets.QMenu):
    """Context menu with common export actions."""

    def __init__(self, plot_widget: pg.PlotWidget):
        super().__init__()
        self._plot_widget = plot_widget
        self.addAction("Export as PNG", self._export_png)
        self.addAction("Copy CSV of visible data", self._copy_csv)

    def _export_png(self):
        exporter = pg.exporters.ImageExporter(self._plot_widget.plotItem)
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self._plot_widget, "Save Image", "", "PNG Files (*.png)"
        )
        if path:
            exporter.export(path)

    def _copy_csv(self):
        lines = []
        for item in self._plot_widget.listDataItems():
            if not item.isVisible():
                continue
            x, y = item.getData()
            for xv, yv in zip(x, y):
                lines.append(f"{xv},{yv}")
        if lines:
            QtWidgets.QApplication.clipboard().setText("\n".join(lines))


class BasePlotWidget(pg.PlotWidget):
    """PlotWidget with legend, context menu and hover tooltip."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.showGrid(x=True, y=True, alpha=0.3)
        self.addLegend(offset=(30, 10))
        self.scene().contextMenu = CustomPlotMenu(self)
        self.scene().sigMouseMoved.connect(self._show_tooltip)

    def _show_tooltip(self, pos):
        if not self.plotItem.sceneBoundingRect().contains(pos):
            return
        mouse_point = self.plotItem.vb.mapSceneToView(pos)
        QtWidgets.QToolTip.showText(
            QtGui.QCursor.pos(),
            f"t={mouse_point.x():.2f}s\nµV={mouse_point.y():.2f}",
        )

