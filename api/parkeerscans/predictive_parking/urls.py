"""predictive_parking ROOT URL Configuration
"""

from rest_framework_swagger.views import get_swagger_view
from rest_framework import routers
from rest_framework.schemas import get_schema_view

from django.conf.urls import url, include
from django.conf import settings


from occupancy import views as occupancy_views
from metingen import views as meting_views
from wegdelen import views as wegdelen_views


class PredictiveParkingView(routers.APIRootView):
    """

    * Messured occupation
    * Aggregation counts for parking spots (vakken)
    * Aggregation counts for roadparts (wegdelen)

    ## WFS

    WFS data of vakken, wegdelen:

    [WFS wegdelen](https://map.data.amsterdam.nl/maps/parkeerscans?REQUEST=GetCapabilities&SERVICE=wfs)

    [WFS parkeervakken](https://map.data.amsterdam.nl/maps/parkeervakken?REQUEST=GetCapabilities&SERVICE=wfs)

    ### Scan data source

    The scan data is cleaned and combines with map data from BGT.
    Every scan within 1.5 meter of an official parking spot
    is counted as parked car.

    source code:
    -----------

    <https://github.com/DatapuntAmsterdam/predictive_parking>
    """  # noqa


class PredictiveParkingRouter(routers.DefaultRouter):
    """The main router"""
    APIRootView = PredictiveParkingView


parkeerscans = PredictiveParkingRouter()

parkeerscans.register(
    r'occupancy/public',
    occupancy_views.OccupancyInBBOX, 'bboxoccupancy')


parkeerscans.register(
    r'occupancy/roadparts',
    occupancy_views.RoadOccupancyViewSet, 'roadoccupancy')

parkeerscans.register(
    r'wegdelen', wegdelen_views.WegdelenViewSet, 'wegdeel')

parkeerscans.register(
    r'vakken', wegdelen_views.VakkenViewSet, 'parkeervak')


parkeerscans.register(
    r'metingen/aggregations/wegdelen',
    meting_views.WegdelenAggregationViewSet, 'wegdelen')


parkeerscans.register(
    r'metingen/aggregations/vakken',
    meting_views.VakkenAggregationViewSet, 'vakken')

parkeerscans.urls.append(url(
    r'voutevakken',
    wegdelen_views.verdachte_vakken_view))

parkeerscans.urls.append(
    url(r'gratis', wegdelen_views.verdachte_bgt_parkeervlak))

# parkeerscans.extend(kansen)
schema_view = get_swagger_view(title='Parkeer Scans')

json_schema_view = get_schema_view(title='Parkeerscan API')
# parkeerscans.register(r'parkeerkans', kansen.urls

urlpatterns = [
    url(r'^status/', include('health.urls')),
    url(r'^schema/', json_schema_view),
    url(r'^parkeerscans/doc', schema_view),
    url(r'^parkeerscans/', include(parkeerscans.urls)),
    # url(r'^metingen/', include(kansen.urls)),
]

if settings.DEBUG:
    import debug_toolbar  # noqa
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls))
    ] + urlpatterns
