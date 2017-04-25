
from datapunt import rest

from . import serializers
from . import models


class MetingenViewSet(rest.DatapuntViewSet):
    """
    Alle scan metingen

    - scan_id
    - scan_moment
    - device_id -  unieke device id / auto id
    - scan_source - auto of pda

    - buurtcode - bag GGW code
    - sperscode - (vergunning..)
    - qualcode- status / kwaliteit
    - nha_nr - naheffings_nummer
    - nha_hoogte - geldboete
    - uitval_nachtrun - nachtelijke correctie

    """

    queryset = models.Scan.objects.all()

    serializer_class = serializers.Scan

    filter_fields = (
        'scan_moment',
        'device_id',
        'scan_source',
        'nha_hoogte',
        'nha_nr',
        'qualcode',
        'buurtcode',
        'sperscode',
        'bgt_wegdeel',
        'bgt_wegdeel_functie',
    )

    ordering = ('scan_id')
