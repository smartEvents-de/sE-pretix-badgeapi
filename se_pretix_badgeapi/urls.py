# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 the sE-pretix authors
from pretix.api.urls import event_router

from .api import BadgeLayoutImportViewSet

# pretix importiert <plugin>.urls beim Start (pretix/api/urls.py), dadurch wird die Route registriert.
urlpatterns = []
event_router.register("badgelayout_import", BadgeLayoutImportViewSet, basename="badgelayout_import")
