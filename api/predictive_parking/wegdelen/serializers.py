from rest_framework_gis.fields import GeometryField

from datapunt import rest

from . import models


class WegDeelList(rest.HALSerializer):

    dataset = 'wegdelen'

    # _display = rest.DisplayField()

    class Meta(object):
        model = models.WegDeel

        fields = (
            '_links',
            # '_display',
            'id',
            'vakken',
            'scan_count',
        )


class WegDeel(rest.HALSerializer):

    dataset = 'wegdelen'

    geometrie = rest.MultipleGeometryField()

    class Meta(object):
        model = models.WegDeel

        fields = (
            '_links',
            'id',
            'vakken',
            'fiscale_vakken',
            'scan_count',
            'bgt_functie',

            'geometrie',
        )
