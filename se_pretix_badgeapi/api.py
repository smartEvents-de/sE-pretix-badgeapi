# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2026 the sE-pretix authors
import json

from django.core.files.base import ContentFile
from django.db import transaction
from rest_framework import serializers, status, viewsets
from rest_framework.response import Response

from pretix.plugins.badges.models import BadgeItem, BadgeLayout

from .validation import ValidationProblem, decode_background, validate_layout

BADGES_PLUGIN = "pretix.plugins.badges"


class BadgeLayoutImportSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=190)
    default = serializers.BooleanField(required=False, default=False)
    layout = serializers.JSONField()
    background_b64 = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    items = serializers.ListField(child=serializers.IntegerField(), required=False, default=list)

    def validate_layout(self, value):
        try:
            return validate_layout(value)
        except ValidationProblem as e:
            raise serializers.ValidationError(str(e))

    def validate_background_b64(self, value):
        try:
            decode_background(value)
        except ValidationProblem as e:
            raise serializers.ValidationError(str(e))
        return value


class BadgeLayoutImportViewSet(viewsets.GenericViewSet):
    """
    POST …/events/<event>/badgelayout_import/

    Legt ein Badge-Layout an (Name, Layout-JSON, optional Hintergrund-PDF als Base64, Produkt-IDs).
    Existiert bereits ein Layout mit diesem Namen, antwortet der Endpunkt mit 409 (nichts wird überschrieben).
    """
    serializer_class = BadgeLayoutImportSerializer
    queryset = BadgeLayout.objects.none()
    permission = "event.settings.general:write"
    write_permission = "event.settings.general:write"

    def create(self, request, *args, **kwargs):
        event = request.event
        if BADGES_PLUGIN not in event.get_plugins():
            return Response(
                {"detail": "Das Plugin 'Badges' ist für dieses Event nicht aktiv."},
                status=status.HTTP_409_CONFLICT,
            )

        ser = self.get_serializer(data=request.data)
        ser.is_valid(raise_exception=True)
        d = ser.validated_data

        if event.badge_layouts.filter(name=d["name"]).exists():
            return Response({"detail": f"Layout '{d['name']}' existiert bereits."}, status=status.HTTP_409_CONFLICT)

        items = list(event.items.filter(pk__in=d["items"]))
        missing = set(d["items"]) - {i.pk for i in items}
        if missing:
            return Response({"items": [f"Unbekannte Produkt-IDs: {sorted(missing)}"]}, status=status.HTTP_400_BAD_REQUEST)

        background = decode_background(d.get("background_b64"))
        with transaction.atomic():
            make_default = d["default"] or not event.badge_layouts.filter(default=True).exists()
            if make_default:
                event.badge_layouts.filter(default=True).update(default=False)
            layout = BadgeLayout.objects.create(
                event=event, name=d["name"], default=make_default, layout=json.dumps(d["layout"]),
            )
            if background:
                layout.background.save("background.pdf", ContentFile(background))
            for item in items:
                BadgeItem.objects.update_or_create(item=item, defaults={"layout": layout})
            layout.log_action(
                "pretix.plugins.badges.layout.added", user=request.user, auth=request.auth,
                data={"name": d["name"], "source": "se_pretix_badgeapi", "items": [i.pk for i in items]},
            )
        return Response(
            {"id": layout.pk, "name": layout.name, "default": layout.default,
             "items": [i.pk for i in items], "has_background": bool(background)},
            status=status.HTTP_201_CREATED,
        )
