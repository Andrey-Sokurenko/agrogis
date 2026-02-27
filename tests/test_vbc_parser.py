from __future__ import annotations

import logging

import pytest

from agro_gis.core.exceptions import EmptyDataError
from agro_gis.core.vbc_parser import VbcParser


def test_parse_csv_comma(tmp_path):
    path = tmp_path / "points.vbc"
    path.write_text("55.7,37.6,10\n56.1,38.2,11", encoding="utf-8")
    gdf = VbcParser().parse(path)
    assert len(gdf) == 2


def test_parse_csv_tab(tmp_path):
    path = tmp_path / "points_tab.vbc"
    path.write_text("55.7\t37.6\t10", encoding="utf-8")
    gdf = VbcParser().parse(path)
    assert len(gdf) == 1


def test_parse_csv_semicolon(tmp_path):
    path = tmp_path / "points_semi.vbc"
    path.write_text("55.7;37.6;10", encoding="utf-8")
    gdf = VbcParser().parse(path)
    assert len(gdf) == 1


def test_geodataframe_geometry_and_crs(tmp_path):
    path = tmp_path / "points.vbc"
    path.write_text("55.7,37.6", encoding="utf-8")
    gdf = VbcParser().parse(path)
    assert gdf.crs.to_string() == "EPSG:4326"
    assert gdf.geometry.iloc[0].geom_type == "Point"


def test_skip_invalid_rows_with_warning(tmp_path, caplog):
    path = tmp_path / "invalid_rows.vbc"
    path.write_text("100,10\n55,200\n55,37", encoding="utf-8")
    caplog.set_level(logging.WARNING)
    gdf = VbcParser().parse(path)
    assert len(gdf) == 1
    assert any("Skipping row out of range" in r.message for r in caplog.records)


def test_empty_data_error(tmp_path):
    path = tmp_path / "empty.vbc"
    path.write_text("# comment\n\nnot,a,coord", encoding="utf-8")
    with pytest.raises(EmptyDataError):
        VbcParser().parse(path)


def test_parse_cp1251_fixture(vbc_cp1251_file):
    gdf = VbcParser().parse(vbc_cp1251_file)
    assert len(gdf) == 2


def test_parse_utf16le_bom_fixture(vbc_utf16le_file):
    gdf = VbcParser().parse(vbc_utf16le_file)
    assert len(gdf) == 2
