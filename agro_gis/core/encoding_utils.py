from __future__ import annotations

import logging
from pathlib import Path

from charset_normalizer import from_bytes

from .exceptions import EncodingDetectionError

logger = logging.getLogger(__name__)

FALLBACK_ENCODINGS = ["utf-8", "cp1251", "cp866", "latin-1"]
MANUAL_CHOICES = ["UTF-8", "CP1251", "CP866", "Latin-1", "UTF-16"]
SUPPORTED_DETECTED_ENCODINGS = {"utf-8", "utf_8", "cp1251", "windows-1251", "cp866", "latin-1", "latin_1", "utf-16", "utf_16", "utf-16le", "utf-16be", "utf_16_le", "utf_16_be"}


def _strip_bom(data: bytes) -> bytes:
    if data.startswith(b"\xef\xbb\xbf"):
        return data[3:]
    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        return data[2:]
    return data


def _text_quality(text: str) -> float:
    if not text:
        return 1.0
    printable_ratio = sum(1 for ch in text if ch.isprintable() or ch in "\n\r\t") / len(text)
    control_ratio = sum(1 for ch in text if ord(ch) < 32 and ch not in "\n\r\t") / len(text)
    alpha_chars = [ch for ch in text if ch.isalpha()]
    alnum_ratio = sum(1 for ch in text if ch.isalnum()) / len(text)
    cyr_ratio = 0.0
    if alpha_chars:
        cyr_ratio = sum(1 for ch in alpha_chars if "\u0400" <= ch <= "\u04FF") / len(alpha_chars)
    score = printable_ratio - control_ratio + (0.6 * cyr_ratio) + (0.2 * alnum_ratio)
    if len(text) >= 4 and alnum_ratio < 0.3:
        score -= 0.5
    return max(0.0, score)


def detect_encoding(data: bytes) -> tuple[str, float]:
    if not data:
        logger.debug("Empty byte stream, defaulting to utf-8")
        return "utf-8", 1.0

    if data.startswith(b"\xef\xbb\xbf"):
        logger.debug("Detected UTF-8 BOM")
        return "utf-8-sig", 1.0
    if data.startswith(b"\xff\xfe") or data.startswith(b"\xfe\xff"):
        logger.debug("Detected UTF-16 BOM")
        return "utf-16", 1.0

    candidate_encodings: list[str] = []
    best = from_bytes(data).best()
    detector_confidence = 0.0
    if best is not None and best.encoding:
        detector_encoding = best.encoding.lower()
        detector_confidence = 1.0 - (best.chaos if best.chaos is not None else 1.0)
        logger.debug("Detected encoding=%s confidence=%.3f", detector_encoding, detector_confidence)
        if detector_encoding in SUPPORTED_DETECTED_ENCODINGS and not detector_encoding.startswith("utf_16") and not detector_encoding.startswith("utf-16"):
            candidate_encodings.append(detector_encoding)

    for enc in FALLBACK_ENCODINGS:
        if enc not in candidate_encodings:
            candidate_encodings.append(enc)

    best_encoding: str | None = None
    best_score = -1.0
    for enc in candidate_encodings:
        try:
            decoded = data.decode(enc)
        except UnicodeDecodeError:
            continue
        score = _text_quality(decoded)
        if enc == "latin-1":
            score -= 0.05
        if score > best_score:
            best_score = score
            best_encoding = enc

    if best_encoding is None or best_score < 0.75:
        raise EncodingDetectionError("Unable to detect/decode file encoding")

    confidence = max(detector_confidence, best_score)
    logger.debug("Selected encoding=%s confidence=%.3f", best_encoding, confidence)
    return best_encoding, confidence


def read_text(path: str | Path, forced_encoding: str | None = None) -> tuple[str, str, float]:
    file_path = Path(path)
    raw = file_path.read_bytes()

    if forced_encoding:
        try:
            text = raw.decode(forced_encoding)
        except UnicodeDecodeError as exc:
            raise EncodingDetectionError(f"Failed to decode with forced encoding {forced_encoding}") from exc
        return text.lstrip("\ufeff"), forced_encoding, 1.0

    encoding, confidence = detect_encoding(raw)
    try:
        text = raw.decode(encoding)
    except UnicodeDecodeError as exc:
        raise EncodingDetectionError(f"Unable to decode {file_path}") from exc

    return text.lstrip("\ufeff"), encoding, confidence
