from __future__ import annotations

import logging
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal

from agro_gis.core.exceptions import EncodingDetectionError, ParseError, WindowsRegistryFileError
from agro_gis.core.map_model import MapModel
from agro_gis.core.reg_parser import RegParser
from agro_gis.core.vbc_parser import VbcParser

logger = logging.getLogger(__name__)


@dataclass(eq=False)
class MapViewModel(QObject):
    map_model: MapModel
    reg_parser: RegParser
    vbc_parser: VbcParser

    layers_changed = Signal()
    error_occurred = Signal(str)
    warning_occurred = Signal(str)

    def __post_init__(self) -> None:
        super().__init__()

    def load_reg(self, path: str, encoding: str | None = None) -> None:
        try:
            gdf = self.reg_parser.parse(path, forced_encoding=encoding)
            self.map_model.add_layer("Map", gdf, style={"color": "#3388cc", "alpha": 0.45})
            self.layers_changed.emit()
        except (WindowsRegistryFileError, ParseError, EncodingDetectionError) as exc:
            logger.error("Failed to load .reg file %s", path, exc_info=True)
            self.error_occurred.emit(str(exc))
            raise

    def load_vbc(self, path: str, encoding: str | None = None) -> None:
        try:
            gdf = self.vbc_parser.parse(path, forced_encoding=encoding)
            self.map_model.add_layer("Points", gdf, style={"color": "#dd3333", "size": 24, "alpha": 0.9})
            self.layers_changed.emit()
        except Exception as exc:
            logger.error("Failed to load .vbc file %s", path, exc_info=True)
            self.error_occurred.emit(str(exc))
            raise
