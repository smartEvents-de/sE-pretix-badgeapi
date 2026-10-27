# sE-pretix-badgeapi

pretix-Plugin (Kategorie „API features“). Die pretix-REST-API kennt Badges nur lesend (`badgelayouts/` ist ein
`ReadOnlyModelViewSet`). Dieses Plugin ergänzt einen Schreib-Endpunkt zum Anlegen von Badge-Layouts per API (z. B. um Events zwischen pretix-Instanzen zu kopieren).

## Endpunkt

`POST /api/v1/organizers/<org>/events/<event>/badgelayout_import/`  (Team-Token mit „Event-Einstellungen ändern“)

```json
{
  "name": "Badge A",
  "default": false,
  "layout": [{"type": "textarea", "content": "attendee_name", "left": "13", "bottom": "50", "...": "..."}],
  "background_b64": "<PDF als Base64, optional, max. 15 MB>",
  "items": [123, 124]
}
```

- 201: `{"id", "name", "default", "items", "has_background"}`; 409: Layout gleichen Namens existiert oder Plugin „Badges“ im Event inaktiv;
  400: Layout/Hintergrund/Produkt-IDs ungültig. Nichts wird überschrieben. Aktion wird im Event-Log protokolliert.
- Das Plugin muss im Event **aktiv** sein (Plugins-Seite) und `pretix.plugins.badges` ebenfalls.

## Installation

```bash
pip install se-pretix-badgeapi        # bzw. aus dem Quellcode: pip install .
# danach pretix neu starten; Docker: Zeile `RUN pip3 install …` im eigenen Dockerfile (auf Basis von pretix/standalone)
```

Das Plugin (Modul `se_pretix_badgeapi`) erscheint in der Plugin-Liste des Events. Kein Datenbank-Modell, keine Migrationen.

## Kompatibilität

`PretixPluginMeta.compatibility = "pretix>=2026.8.0,<2027.0.0"`. Passt die installierte pretix-Version nicht, **beendet pretix den Start**
(`PluginConfig.__init__`). Nach jedem pretix-Versionswechsel Tests laufen lassen und prüfen, ob `BadgeLayout`/`BadgeItem` unverändert sind.

## Tests

```bash
python -m venv .venv && .venv/bin/pip install pytest && .venv/bin/python -m pytest tests/test_validation.py -q   # standalone
# API-Tests (tests/test_api.py): im pretix-Repo mit installiertem Plugin
```

## Lizenz

GNU Affero General Public License v3 oder später (siehe `LICENSE`). Das Plugin ist ein abgeleitetes Werk von pretix und
steht deshalb ebenfalls unter der AGPL. Für den Betrieb von pretix gelten zusätzlich die
[Zusatzbedingungen von pretix](https://github.com/pretix/pretix/blob/master/LICENSE).

**Inoffiziell:** Dieses Projekt wird nicht vom pretix-Team entwickelt oder unterstützt. „pretix“ ist eine Marke von rami.io GmbH.
