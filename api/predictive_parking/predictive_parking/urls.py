"""predictive_parking ROOT URL Configuration
"""

from rest_framework import routers

from django.conf.urls import url, include


class MetingenScanRouter(routers.DefaultRouter):
    """
    Parkeerscan data

    De scandata die gebruikt wordt voor analyses.

    De data is dermate groot dat er beter niet direct met deze API
    gewerkt kan worden.

    Filteren kan op tijd, soort, type, scan, device_id.

    De dataset groeit met ongeveer 3.000.000 per maand.
    begin 2017 zijn er al 43.000.000 scans beschikbaar voor analyses.
    """

    def get_api_root_view(self, **kwargs):
        view = super().get_api_root_view(**kwargs)
        cls = view.cls

        class ParkeerScans(cls):
            pass

        # Typeahead.__doc__ = self.__doc__
        # return Typeahead.as_view()


scans = MetingenScanRouter()

urlpatterns = [
    url(r'^status/', include('health.urls', namespace='health')),
    # url(r'^metingen/', include(scans.urls)),
]
