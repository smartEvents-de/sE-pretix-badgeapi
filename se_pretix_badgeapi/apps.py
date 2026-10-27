# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 the sE-pretix authors
from django.utils.translation import gettext_lazy as _

from . import __version__

try:
    from pretix.base.plugins import PluginConfig
except ImportError:  # pragma: no cover
    raise RuntimeError("Dieses Plugin braucht pretix (>= 2026.8).")


class PluginApp(PluginConfig):
    default = True
    name = "se_pretix_badgeapi"
    verbose_name = _("Badge API")

    class PretixPluginMeta:
        name = _("Badge API (Schreibzugriff)")
        author = "sE-pretix"
        version = __version__
        category = "API"
        visible = True
        description = _(
            "Stellt einen REST-Endpunkt bereit, mit dem Badge-Layouts (inklusive Hintergrund und "
            "Produktzuordnung) per API-Token angelegt werden können. Die pretix-API selbst liest Badges nur."
        )
        compatibility = "pretix>=2026.8.0,<2027.0.0"
