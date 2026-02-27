from __future__ import annotations

import logging
from dataclasses import dataclass, field

import geopandas as gpd

logger = logging.getLogger(__name__)

DEFAULT_CRS = "EPSG:4326"
RENDER_CRS = "EPSG:3857"


@dataclass
class Layer:
    name: str
    gdf: gpd.GeoDataFrame
    visible: bool = True
    style: dict = field(default_factory=dict)


class MapModel:
    def __init__(self) -> None:
        self.layers: list[Layer] = []

    def _normalize_crs(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        out = gdf.copy()
        if out.crs is None:
            logger.warning("Layer without CRS detected; defaulting to EPSG:4326")
            out = out.set_crs(DEFAULT_CRS)
        elif out.crs.to_string() != DEFAULT_CRS:
            logger.info("Converting layer CRS from %s to %s", out.crs, DEFAULT_CRS)
            out = out.to_crs(DEFAULT_CRS)
        return out

    def add_layer(self, name: str, gdf: gpd.GeoDataFrame, style: dict | None = None) -> None:
        norm = self._normalize_crs(gdf)
        self.layers.append(Layer(name=name, gdf=norm, style=style or {}))

    def remove_layer(self, index: int) -> None:
        self.layers.pop(index)

    def move_layer(self, old_index: int, new_index: int) -> None:
        layer = self.layers.pop(old_index)
        self.layers.insert(new_index, layer)

    def set_visibility(self, index: int, visible: bool) -> None:
        self.layers[index].visible = visible

    def get_visible_layers_for_render(self) -> list[Layer]:
        visible = [layer for layer in self.layers if layer.visible]
        result: list[Layer] = []
        for layer in visible:
            rendered = layer.gdf.to_crs(RENDER_CRS)
            result.append(Layer(name=layer.name, gdf=rendered, visible=True, style=layer.style))
        return result

    def reproject_point_to_wgs84(self, x: float, y: float, source_crs: str = RENDER_CRS) -> tuple[float, float]:
        temp = gpd.GeoSeries.from_xy([x], [y], crs=source_crs).to_crs(DEFAULT_CRS)
        point = temp.iloc[0]
        return point.y, point.x
