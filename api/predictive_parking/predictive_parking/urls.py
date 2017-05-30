"""predictive_parking ROOT URL Configuration
"""

from parkeerkans import views as kansviews

from rest_framework import routers

from django.conf.urls import url, include
from django.conf import settings


from metingen import views as metingViews
from wegdelen import views as wegdelenViews


class PredictiveParkingView(routers.APIRootView):
    """
    Alle API's / databronnen met betrekking tot predictive parking

    * parkeerkans model output
    * metingen (scans)
    * tellingen mbv elasticsearch

    voor WFS data van vakken , wegdelen en scans:

    [https://acc.map.amsterdam.nl/predictiveparking]
    [https://map.amsterdam.nl/parkeervakken]

    De scan data in deze api is opgeschoond en verrijkt met
    actuele BGT wegdelen informatie en BAG gebieden informatie.
    elke scan is gekoppeld aan een parkeervak uit de parkeervakken
    kaart mits de scan binnen 1.5 meter van een Parkeervak is.
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

predictiveparking.register(
    r'metingen/scans', metingViews.MetingenViewSet, 'scan')

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

# predictiveparking.register(r'parkeerkans', kansen.urls

urlpatterns = [
    url(r'^status/', include('health.urls', namespace='health')),
    url(r'^predictiveparking/', include(predictiveparking.urls)),


    # url(r'^metingen/', include(kansen.urls)),
]

if settings.DEBUG:
    import debug_toolbar  # noqa
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls))
    ] + urlpatterns
