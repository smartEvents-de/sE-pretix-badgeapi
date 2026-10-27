# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 the sE-pretix authors
import base64

import pytest

from se_pretix_badgeapi.validation import (
    MAX_LAYOUT_ELEMENTS, ValidationProblem, decode_background, validate_layout,
)

PDF = b"%PDF-1.4\n%fake"


def test_layout_ok_und_unbekannte_typen_erlaubt():
    el = [{"type": "textarea", "content": "attendee_name"}, {"type": "zukunftstyp"}]
    assert validate_layout(el) == el


@pytest.mark.parametrize("bad", [{}, "x", [1], [{"nope": 1}], [{"type": 5}]])
def test_layout_ungueltig(bad):
    with pytest.raises(ValidationProblem):
        validate_layout(bad)


def test_layout_zu_gross():
    with pytest.raises(ValidationProblem):
        validate_layout([{"type": "textarea"}] * (MAX_LAYOUT_ELEMENTS + 1))


def test_background():
    assert decode_background(None) is None and decode_background("") is None
    assert decode_background(base64.b64encode(PDF).decode()) == PDF
    with pytest.raises(ValidationProblem):
        decode_background("kein base64 !!")
    with pytest.raises(ValidationProblem):
        decode_background(base64.b64encode(b"GIF89a").decode())
