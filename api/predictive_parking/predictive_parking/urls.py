"""predictive_parking ROOT URL Configuration
"""

from parkeerkans import views as kansviews

from rest_framework import routers

from django.conf.urls import url, include
from django.conf import settings


from metingen import views as metingviews


class PredictiveParkingView(routers.APIRootView):
    """
    Alle API's / databronnen met betrekking tot predictive parking

    * parkeerkans model output
    * metingen (scans)
    * tellingen mbv elasticsearch

    voor WFS data van vakken , wegdelen en scans:

    [https://acc.map.amsterdam.nl/predictiveparking]

    """


class PredictiveParkingRouter(routers.DefaultRouter):
    APIRootView = PredictiveParkingView


# kansen.register(r'kansen/', kansviews.KansmodelViewSet, base_name='mvp')


predictiveparking = PredictiveParkingRouter()

predictiveparking.register(r'kansen/buurt', kansviews.KansmodelViewSet, 'mvp')
predictiveparking.register(
    r'metingen/scans', metingviews.MetingenViewSet, 'scan')

predictiveparking.register(
    r'metingen/aggregations/wegdelen',
    metingviews.WegdelenAggregationViewSet, 'wegdelen')


predictiveparking.register(
    r'metingen/aggregations/vakkenn',
    metingviews.VakkenAggregationViewSet, 'vakken')


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
