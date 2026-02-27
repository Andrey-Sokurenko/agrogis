from __future__ import annotations

import pytest

from agro_gis.core.exceptions import ParseError, WindowsRegistryFileError
from agro_gis.core.reg_parser import RegParser


def test_parse_valid_wkt(tmp_path):
    path = tmp_path / "map.reg"
    path.write_text("POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))", encoding="utf-8")
    gdf = RegParser().parse(path)
    assert len(gdf) == 1


def test_parse_valid_bbox(tmp_path):
    path = tmp_path / "bbox.reg"
    path.write_text("10,20,30,40", encoding="utf-8")
    gdf = RegParser().parse(path)
    assert len(gdf) == 1


def test_parse_valid_geojson(tmp_path):
    path = tmp_path / "geojson.reg"
    path.write_text(
        '{"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[37.6,55.7]},"properties":{"id":1}}]}',
        encoding="utf-8",
    )
    gdf = RegParser().parse(path)
    assert len(gdf) == 1


def test_reject_windows_registry_file(tmp_path):
    path = tmp_path / "registry.reg"
    path.write_text("Windows Registry Editor Version 5.00\n[HKEY_LOCAL_MACHINE]", encoding="utf-8")
    with pytest.raises(WindowsRegistryFileError):
        RegParser().parse(path)


def test_parse_error_unknown_format(tmp_path):
    path = tmp_path / "unknown.reg"
    path.write_text("totally unknown text", encoding="utf-8")
    with pytest.raises(ParseError):
        RegParser().parse(path)


def test_parse_cp866_fixture(reg_cp866_file):
    gdf = RegParser().parse(reg_cp866_file)
    assert len(gdf) == 1
