# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 the sE-pretix authors
"""API-Tests im Stil der pretix-Testsuite. Laufen NICHT standalone, sondern im pretix-Repo
(`src/`, mit `pytest tests/plugins/...`), wenn dieses Plugin dort installiert ist:

    pip install -e ../se-pretix-badgeapi && cd pretix/src && pytest <pfad>/tests/test_api.py

Ohne pretix werden sie übersprungen.
"""
import base64
import json

import pytest

pytest.importorskip("pretix")
pytest.importorskip("pretix.plugins.badges")

from django_scopes import scopes_disabled  # noqa: E402
from pretix.base.models import Event, Item, Organizer, Team  # noqa: E402
from pretix.plugins.badges.models import BadgeItem, BadgeLayout  # noqa: E402

PDF = base64.b64encode(b"%PDF-1.4\n%fake").decode()


@pytest.fixture
def env(db):
    from datetime import datetime, timezone
    o = Organizer.objects.create(name="Org", slug="org")
    e = Event.objects.create(organizer=o, name="E", slug="e", date_from=datetime(2030, 1, 1, tzinfo=timezone.utc),
                             plugins="pretix.plugins.badges,se_pretix_badgeapi")
    t = Team.objects.create(organizer=o, name="T", all_events=True, can_change_event_settings=True)
    token = t.tokens.create(name="x")
    with scopes_disabled():
        item = Item.objects.create(event=e, name="Ticket", default_price=10)
    return e, item, token


def post(client, token, e, data):
    client.credentials(HTTP_AUTHORIZATION="Token " + token.token)
    return client.post(f"/api/v1/organizers/org/events/{e.slug}/badgelayout_import/", data, format="json")


def test_anlegen(client, env):
    from rest_framework.test import APIClient
    e, item, token = env
    r = post(APIClient(), token, e, {
        "name": "Badge A", "default": True, "layout": [{"type": "textarea", "content": "attendee_name"}],
        "background_b64": PDF, "items": [item.pk],
    })
    assert r.status_code == 201, r.content
    with scopes_disabled():
        bl = BadgeLayout.objects.get(event=e, name="Badge A")
        assert bl.default and bl.background and json.loads(bl.layout)[0]["type"] == "textarea"
        assert BadgeItem.objects.get(item=item).layout == bl


def test_duplikat_und_fehler(client, env):
    from rest_framework.test import APIClient
    e, item, token = env
    c = APIClient()
    body = {"name": "B", "layout": [{"type": "textarea"}]}
    assert post(c, token, e, body).status_code == 201
    assert post(c, token, e, body).status_code == 409
    assert post(c, token, e, {"name": "C", "layout": "kaputt"}).status_code == 400
    assert post(c, token, e, {**body, "name": "D", "items": [999999]}).status_code == 400


def test_ohne_berechtigung(client, env):
    from rest_framework.test import APIClient
    e, item, token = env
    token.team.can_change_event_settings = False
    token.team.save()
    assert post(APIClient(), token, e, {"name": "B", "layout": []}).status_code == 403
