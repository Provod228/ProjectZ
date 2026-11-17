from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import BoardModelViewSet, ColumnListView, TaskListView

router = DefaultRouter()
router.register('boards', BoardModelViewSet, basename='board')

urlpatterns = router.urls + [
    path('boards/<int:board_pk>/columns/', ColumnListView.as_view(), name='board-columns'),
    path('columns/<int:column_pk>/tasks/', TaskListView.as_view(), name='column-tasks'),
]