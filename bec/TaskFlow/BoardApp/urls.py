from rest_framework.routers import DefaultRouter

from .views import BoardModelViewSet

router = DefaultRouter()
router.register('boards', BoardModelViewSet, basename='board')

urlpatterns = router.urls