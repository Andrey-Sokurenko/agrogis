from __future__ import annotations

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely import wkt
from shapely.geometry import Polygon, shape

from .encoding_utils import read_text
from .exceptions import ParseError, WindowsRegistryFileError

logger = logging.getLogger(__name__)


class RegParseStrategy(ABC):
    @abstractmethod
    def parse(self, text: str) -> gpd.GeoDataFrame:
        raise NotImplementedError


class WktPolygonStrategy(RegParseStrategy):
    def parse(self, text: str) -> gpd.GeoDataFrame:
        geoms = []
        for line in text.splitlines():
            clean = line.strip()
            if not clean:
                continue
            geom = wkt.loads(clean)
            geoms.append(geom)
        if not geoms:
            raise ValueError("No WKT geometries")
        return gpd.GeoDataFrame({"name": ["wkt"] * len(geoms)}, geometry=geoms, crs="EPSG:4326")


class BboxStrategy(RegParseStrategy):
    def parse(self, text: str) -> gpd.GeoDataFrame:
        tokens = [tok for tok in text.replace("\n", " ").replace(",", " ").split() if tok]
        if len(tokens) != 4:
            raise ValueError("Expected exactly 4 bbox values")
        minx, miny, maxx, maxy = map(float, tokens)
        if minx >= maxx or miny >= maxy:
            raise ValueError("Invalid bbox ranges")
        geom = Polygon([(minx, miny), (maxx, miny), (maxx, maxy), (minx, maxy)])
        return gpd.GeoDataFrame({"name": ["bbox"]}, geometry=[geom], crs="EPSG:4326")


class GeoJsonLikeStrategy(RegParseStrategy):
    def parse(self, text: str) -> gpd.GeoDataFrame:
        payload = json.loads(text)
        if payload.get("type") == "FeatureCollection":
            features = payload.get("features", [])
            geoms = [shape(feat["geometry"]) for feat in features]
            props = [feat.get("properties", {}) for feat in features]
            return gpd.GeoDataFrame(props if props else [{}], geometry=geoms, crs="EPSG:4326")
        if payload.get("type") in {"Polygon", "MultiPolygon", "Point", "LineString"}:
            geom = shape(payload)
            return gpd.GeoDataFrame({"name": ["geojson"]}, geometry=[geom], crs="EPSG:4326")
        raise ValueError("Unsupported GeoJSON payload")


class CsvCoordinatesStrategy(RegParseStrategy):
    def parse(self, text: str) -> gpd.GeoDataFrame:
        rows = []
        for line in text.splitlines():
            clean = line.strip()
            if not clean:
                continue
            parts = [p.strip() for p in clean.split(",")]
            if len(parts) < 2:
                continue
            x, y = float(parts[0]), float(parts[1])
            rows.append((x, y))
        if len(rows) < 3:
            raise ValueError("Need at least 3 coordinate rows for polygon")
        if rows[0] != rows[-1]:
            rows.append(rows[0])
        geom = Polygon(rows)
        if geom.is_empty or not geom.is_valid:
            raise ValueError("Invalid geometry built from CSV")
        return gpd.GeoDataFrame(pd.DataFrame([{"name": "csv"}]), geometry=[geom], crs="EPSG:4326")


class RegParser:
    def __init__(self, strategies: list[RegParseStrategy] | None = None) -> None:
        self.strategies = strategies or [
            WktPolygonStrategy(),
            BboxStrategy(),
            GeoJsonLikeStrategy(),
            CsvCoordinatesStrategy(),
        ]

    def parse(self, path: str | Path, forced_encoding: str | None = None) -> gpd.GeoDataFrame:
        text, encoding, confidence = read_text(path, forced_encoding=forced_encoding)
        logger.debug("Loaded REG file %s encoding=%s confidence=%.3f", path, encoding, confidence)

        first_nonempty = next((line.strip() for line in text.splitlines() if line.strip()), "")
        if "Windows Registry Editor" in first_nonempty:
            raise WindowsRegistryFileError("Provided .reg file is a Windows Registry export")

        errors: list[str] = []
        for strategy in self.strategies:
            name = strategy.__class__.__name__
            try:
                gdf = strategy.parse(text)
                return gdf
            except Exception as exc:
                errors.append(f"{name}: {exc}")

        raise ParseError("Unable to parse .reg file. Attempts: " + "; ".join(errors))
