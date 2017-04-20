from . import views as kansviews

router = routers.DefaultRouter()


router.register(r'kansen/', kansviews.KansmodelViewSet, 'mvp')
