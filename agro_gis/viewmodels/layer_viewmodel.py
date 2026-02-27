from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal

from agro_gis.core.map_model import MapModel


@dataclass(eq=False)
class LayerViewModel(QObject):
    map_model: MapModel

    layers_changed = Signal()

    def __post_init__(self) -> None:
        super().__init__()

    def set_layer_visibility(self, index: int, visible: bool) -> None:
        self.map_model.set_visibility(index, visible)
        self.layers_changed.emit()

    def remove_layer(self, index: int) -> None:
        self.map_model.remove_layer(index)
        self.layers_changed.emit()

    def move_layer(self, old: int, new: int) -> None:
        self.map_model.move_layer(old, new)
        self.layers_changed.emit()
