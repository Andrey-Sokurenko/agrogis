from __future__ import annotations

import logging
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from .encoding_utils import read_text
from .exceptions import EmptyDataError

logger = logging.getLogger(__name__)


class VbcParser:
    DELIMITERS = [",", ";", "\t", " "]

    def parse(self, path: str | Path, forced_encoding: str | None = None) -> gpd.GeoDataFrame:
        text, encoding, confidence = read_text(path, forced_encoding=forced_encoding)
        logger.debug("Loaded VBC file %s encoding=%s confidence=%.3f", path, encoding, confidence)
        lines = [line.strip() for line in text.splitlines()]

        data_rows: list[dict] = []
        for line in lines:
            if not line or line.startswith("#"):
                continue
            tokens = self._split_line(line)
            if len(tokens) < 2:
                logger.warning("Skipping malformed row (not enough columns): %s", line)
                continue

            try:
                lat = float(tokens[0])
                lon = float(tokens[1])
            except ValueError:
                logger.warning("Skipping malformed row (non-numeric coordinates): %s", line)
                continue

            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                logger.warning("Skipping row out of range lat/lon: %s", line)
                continue

            extras = tokens[2:]
            row = {"lat": lat, "lon": lon, "_extras": extras}
            data_rows.append(row)

        if not data_rows:
            raise EmptyDataError("No valid VBC rows found")

        max_extra = max(len(r["_extras"]) for r in data_rows)
        records = []
        for row in data_rows:
            rec = {"lat": row["lat"], "lon": row["lon"]}
            for idx in range(max_extra):
                value = row["_extras"][idx] if idx < len(row["_extras"]) else None
                rec[f"value{idx + 1}"] = value
            records.append(rec)

        df = pd.DataFrame.from_records(records)
        gdf = gpd.GeoDataFrame(df, geometry=[Point(xy) for xy in zip(df["lon"], df["lat"])], crs="EPSG:4326")
        return gdf

    def _split_line(self, line: str) -> list[str]:
        for delimiter in self.DELIMITERS:
            if delimiter == " ":
                parts = [item for item in line.split() if item]
            else:
                parts = [item.strip() for item in line.split(delimiter)]
            if len(parts) >= 2:
                return parts
        return []
