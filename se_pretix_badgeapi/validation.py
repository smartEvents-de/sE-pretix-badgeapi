# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 the sE-pretix authors
"""Reine Python-Validierung (ohne pretix/Django-Import), damit sie isoliert testbar ist."""
from __future__ import annotations

import base64
import binascii

MAX_LAYOUT_ELEMENTS = 500
MAX_BACKGROUND_BYTES = 15 * 1024 * 1024
# Elementtypen laut pretix/base/pdf.py (Renderer). Unbekannte Typen lehnen wir nicht ab (neuere
# pretix-Versionen können weitere kennen), sie werden nur strukturell geprüft.
KNOWN_TYPES = {"textarea", "textcontainer", "barcodearea", "imagearea", "poweredby"}


class ValidationProblem(ValueError):
    pass


def validate_layout(layout) -> list:
    """Badge-Layout: Liste von Elementen (dicts mit 'type')."""
    if not isinstance(layout, list):
        raise ValidationProblem("layout muss eine Liste von Elementen sein.")
    if len(layout) > MAX_LAYOUT_ELEMENTS:
        raise ValidationProblem(f"layout hat zu viele Elemente (max. {MAX_LAYOUT_ELEMENTS}).")
    for i, el in enumerate(layout):
        if not isinstance(el, dict) or "type" not in el:
            raise ValidationProblem(f"layout[{i}] ist kein Element mit 'type'.")
        if not isinstance(el["type"], str):
            raise ValidationProblem(f"layout[{i}]: 'type' muss Text sein.")
    return layout


def decode_background(b64: str | None) -> bytes | None:
    """Base64-PDF -> Bytes (oder None). Prüft PDF-Signatur und Größe."""
    if not b64:
        return None
    try:
        raw = base64.b64decode(b64, validate=True)
    except (binascii.Error, ValueError):
        raise ValidationProblem("background_b64 ist kein gültiges Base64.")
    if len(raw) > MAX_BACKGROUND_BYTES:
        raise ValidationProblem("background_b64 ist zu groß (max. 15 MB).")
    if not raw.startswith(b"%PDF"):
        raise ValidationProblem("background_b64 ist kein PDF.")
    return raw
