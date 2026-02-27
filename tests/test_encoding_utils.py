from __future__ import annotations

import pytest

from agro_gis.core.encoding_utils import read_text
from agro_gis.core.exceptions import EncodingDetectionError


def test_detect_utf8(utf8_file):
    text, encoding, confidence = read_text(utf8_file)
    assert "Привет" in text
    assert encoding
    assert confidence > 0


def test_detect_cp1251(cp1251_file):
    text, encoding, _ = read_text(cp1251_file)
    assert "Привет" in text
    assert encoding.lower() in {"cp1251", "windows-1251", "utf_16_be", "utf_16_le", "utf-16be", "utf-16le", "utf-8"}


def test_detect_cp866(cp866_file):
    text, _, _ = read_text(cp866_file)
    assert "Тест" in text


def test_strip_utf8_bom(utf8_bom_file):
    text, _, _ = read_text(utf8_bom_file)
    assert text.startswith("данные")


def test_strip_utf16le_bom(utf16le_bom_file):
    text, encoding, _ = read_text(utf16le_bom_file)
    assert "координаты" in text
    assert "utf-16" in encoding.lower()


def test_encoding_detection_error(tmp_path):
    bad = tmp_path / "bad.bin"
    bad.write_bytes(b"\x00\x01\x02\x03\x04")
    with pytest.raises(EncodingDetectionError):
        read_text(bad)
