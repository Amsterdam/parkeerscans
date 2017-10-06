"""predictive_parking ROOT URL Configuration
"""

from parkeerkans import views as kansviews

from rest_framework_swagger.views import get_swagger_view
from rest_framework import routers
from rest_framework.schemas import get_schema_view

from django.conf.urls import url, include
from django.conf import settings


from metingen import views as metingViews
from wegdelen import views as wegdelenViews


class PredictiveParkingView(routers.APIRootView):
    """
    Data-sources related to predictive parking

    * parking probaility model output (not finished)
    * aggregation counts for parking spots (vakken)
    # aggregation counts for roadparts (wegdelen)

    WFS data of vakken, wegdelen:

    [https://acc.map.amsterdam.nl/predictiveparking]
    [https://map.amsterdam.nl/parkeervakken]

    De scan data in deze api is opgeschoond en verrijkt met
    actuele BGT wegdelen informatie en BAG gebieden informatie.
    elke scan is gekoppeld aan een parkeervak uit de parkeervakken
    kaart mits de scan binnen 1.5 meter van een Parkeervak is.

    The scan data is cleaned and combines with map data from BGT.
    Every scan within 1.5 meter of an official parking spot
    is counted as parked car.

    source code:
    [https://github.com/DatapuntAmsterdam/predictive_parking/tree/master/api]
    [https://github.com/DatapuntAmsterdam/predictive_parking]
    """


class PredictiveParkingRouter(routers.DefaultRouter):
    """The main router"""
    APIRootView = PredictiveParkingView


# kansen.register(r'kansen/', kansviews.KansmodelViewSet, base_name='mvp')


predictiveparking = PredictiveParkingRouter()

predictiveparking.register(r'kansen/buurt', kansviews.KansmodelViewSet, 'mvp')


predictiveparking.register(
    r'wegdelen', wegdelenViews.WegdelenViewSet, 'wegdeel')

predictiveparking.register(
    r'vakken', wegdelenViews.VakkenViewSet, 'parkeervak')

# mag niet publiek
#predictiveparking.register(
#    r'metingen/scans', metingViews.MetingenViewSet, 'scan')

predictiveparking.register(
    r'metingen/aggregations/wegdelen',
    metingViews.WegdelenAggregationViewSet, 'wegdelen')


predictiveparking.register(
    r'metingen/aggregations/vakken',
    metingViews.VakkenAggregationViewSet, 'vakken')

predictiveparking.urls.append(url(
    r'voutevakken',
    wegdelenViews.verdachte_vakken_view))

predictiveparking.urls.append(
    url(r'gratis', wegdelenViews.verdachte_bgt_parkeervlak))


# predictiveparking.extend(kansen)
schema_view = get_swagger_view(title='Parkeer Scans')

json_schema_view = get_schema_view(title='Parkeerscan API')
# predictiveparking.register(r'parkeerkans', kansen.urls

urlpatterns = [
    url(r'^status/', include('health.urls', namespace='health')),
    url(r'^schema/', json_schema_view),
    url(r'^predictiveparking/doc', schema_view),
    url(r'^predictiveparking/', include(predictiveparking.urls)),


    # url(r'^metingen/', include(kansen.urls)),
]

if settings.DEBUG:
    import debug_toolbar  # noqa
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls))
    ] + urlpatterns
