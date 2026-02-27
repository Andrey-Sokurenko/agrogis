from __future__ import annotations

import pytest


@pytest.fixture
def utf8_file(tmp_path):
    p = tmp_path / "sample_utf8.txt"
    p.write_text("Привет, мир", encoding="utf-8")
    return p


@pytest.fixture
def cp1251_file(tmp_path):
    p = tmp_path / "sample_cp1251.txt"
    p.write_bytes("Привет".encode("cp1251"))
    return p


@pytest.fixture
def cp866_file(tmp_path):
    p = tmp_path / "sample_cp866.txt"
    p.write_bytes("Тест".encode("cp866"))
    return p


@pytest.fixture
def utf8_bom_file(tmp_path):
    p = tmp_path / "sample_utf8_bom.txt"
    p.write_bytes(b"\xef\xbb\xbf" + "данные".encode("utf-8"))
    return p


@pytest.fixture
def utf16le_bom_file(tmp_path):
    p = tmp_path / "sample_utf16le_bom.txt"
    p.write_bytes("координаты".encode("utf-16"))
    return p


@pytest.fixture
def vbc_cp1251_file(tmp_path):
    p = tmp_path / "points_cp1251.vbc"
    content = "# комментарий\n55.7,37.6,10\n56.0,38.0,20\n"
    p.write_bytes(content.encode("cp1251"))
    return p


@pytest.fixture
def vbc_utf16le_file(tmp_path):
    p = tmp_path / "points_utf16.vbc"
    content = "55.7,37.6,10\n56.0,38.0,20\n"
    p.write_bytes(content.encode("utf-16"))
    return p


@pytest.fixture
def reg_cp866_file(tmp_path):
    p = tmp_path / "map_cp866.reg"
    content = "POLYGON ((30 10, 40 40, 20 40, 10 20, 30 10))"
    p.write_bytes(content.encode("cp866"))
    return p
