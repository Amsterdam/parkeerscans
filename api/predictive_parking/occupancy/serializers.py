from rest_framework import serializers
from datapunt_api import rest

from . import models


class Selection(serializers.ModelSerializer):

    class Meta(object):
        model = models.Selection

        fields = '__all__'


class RoadOccupancyList(rest.HALSerializer):

    dataset = 'wegdeelbezetting'

    #_display = rest.DisplayField()

    occupancy = serializers.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    # geometrie = rest.MultipleGeometryField()

    selection = serializers.SerializerMethodField()

    class Meta(object):
        model = models.RoadOccupancy

        fields = (
            '_links',
            # '_display',
            'bgt_id',
            'occupancy',
            'selection',
        )

    def get_selection(self, obj):
        return repr(obj.selection.view_name())


class RoadOccupancy(rest.HALSerializer):

    dataset = 'wegdeelbezetting'

    # _display = rest.DisplayField()

    occupancy = serializers.DecimalField(
        max_digits=5,
        decimal_places=2
    )

    # geometrie = rest.MultipleGeometryField()

    selection = Selection()

    class Meta(object):
        model = models.RoadOccupancy

        fields = (
            '_links',
            # '_display',
            'bgt_id',
            'occupancy',
            'selection',
            # 'geometrie',
        )
