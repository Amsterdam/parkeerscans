from rest_framework import serializers

from rest_framework_gis.fields import GeometryField

from datapunt import rest

from . import models

# from rest_framework.reverse import reverse


class Kansmodel(rest.HALSerializer):

    dataset = 'kansmodel'

    _display = rest.DisplayField()

    verwachte_bezettingsgraad = serializers.DecimalField(
        max_digits=5,
        decimal_places=2)

    # group_geometrie = GeometryField()

    class Meta(object):
        model = models.Mvp

        fields = (
            '_links',
            '_display',
            'naam',
            'weekdag',
            'uur',
            'aantal_fiscale_vakken',
            'betrouwbaarheid',
            'verwachte_bezettingsgraad',
            'vollcode',
            # 'group_geometrie',
            'parkeerkansindicatie',
        )
