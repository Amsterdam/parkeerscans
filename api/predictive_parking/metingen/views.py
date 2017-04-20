from django.shortcuts import render


from . import serializers
from . import models

from datapunt import rest


class MetingenViewSet(rest.DatapuntViewSet):
    """
    Alle scan metingen 

    - 'scan_id'          #
    - 'scan_moment',
    - 'device_id',       # unieke device id / auto id
    - 'scan_source',     # auto of pda

    - 'buurtcode',       # GGW code
    - 'sperscode',       # (vergunning..)
    - 'qualcode',        # status / kwaliteit
    - 'ff_df',           # field of desk
    - 'nha_nr', ignored? # naheffings_nummer
    - 'nha_hoogte',      # geldboete
    - 'uitval_nachtrun'  # nachtelijke correctie
 
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
