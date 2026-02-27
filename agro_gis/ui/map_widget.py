from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from agro_gis.core.map_model import MapModel


class MapWidget(QWidget):
    cursor_coordinates_changed = Signal(float, float)

    def __init__(self, map_model: MapModel, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.map_model = map_model

        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.axes = self.figure.add_subplot(111)

        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)

        self._is_dragging = False
        self._drag_start = None
        self._xlim_on_drag = None
        self._ylim_on_drag = None

        self.canvas.mpl_connect("motion_notify_event", self._on_motion)
        self.canvas.mpl_connect("button_press_event", self._on_press)
        self.canvas.mpl_connect("button_release_event", self._on_release)
        self.canvas.mpl_connect("scroll_event", self._on_scroll)

    def render_layers(self) -> None:
        self.axes.clear()
        for layer in self.map_model.get_visible_layers_for_render():
            kwargs = {
                "color": layer.style.get("color", "#3388cc"),
                "alpha": layer.style.get("alpha", 0.6),
            }
            if "size" in layer.style:
                kwargs["markersize"] = layer.style["size"]
            layer.gdf.plot(ax=self.axes, **kwargs)
        self.axes.set_title("Agro GIS")
        self.axes.set_axis_off()
        self.canvas.draw_idle()

    def zoom(self, factor: float) -> None:
        xlim = self.axes.get_xlim()
        ylim = self.axes.get_ylim()
        x_center = (xlim[0] + xlim[1]) / 2
        y_center = (ylim[0] + ylim[1]) / 2
        width = (xlim[1] - xlim[0]) * factor
        height = (ylim[1] - ylim[0]) * factor
        self.axes.set_xlim(x_center - width / 2, x_center + width / 2)
        self.axes.set_ylim(y_center - height / 2, y_center + height / 2)
        self.canvas.draw_idle()

    def _on_scroll(self, event) -> None:
        if event.button == "up":
            self.zoom(0.8)
        elif event.button == "down":
            self.zoom(1.25)

    def _on_press(self, event) -> None:
        if event.button == 1 and event.inaxes:
            self._is_dragging = True
            self._drag_start = (event.xdata, event.ydata)
            self._xlim_on_drag = self.axes.get_xlim()
            self._ylim_on_drag = self.axes.get_ylim()

    def _on_release(self, event) -> None:
        self._is_dragging = False
        self._drag_start = None

    def _on_motion(self, event) -> None:
        if event.inaxes and event.xdata is not None and event.ydata is not None:
            lat, lon = self.map_model.reproject_point_to_wgs84(event.xdata, event.ydata)
            self.cursor_coordinates_changed.emit(lat, lon)

        if self._is_dragging and event.inaxes and event.xdata is not None and event.ydata is not None:
            dx = event.xdata - self._drag_start[0]
            dy = event.ydata - self._drag_start[1]
            self.axes.set_xlim(self._xlim_on_drag[0] - dx, self._xlim_on_drag[1] - dx)
            self.axes.set_ylim(self._ylim_on_drag[0] - dy, self._ylim_on_drag[1] - dy)
            self.canvas.draw_idle()
