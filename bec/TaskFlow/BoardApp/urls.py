from rest_framework.routers import DefaultRouter
from django.urls import path

from BoardApp.views.boards import BoardModelViewSet
from BoardApp.views.columns import ColumnListView, ColumnDetailView
from BoardApp.views.comments import CommentListView, CommentDetailView
from BoardApp.views.tasks import TaskListView, TaskDetailView

router = DefaultRouter()
router.register('boards', BoardModelViewSet, basename='board')

urlpatterns = router.urls + [
    path('boards/<int:board_pk>/columns/', ColumnListView.as_view(), name='board-columns'),
    path('boards/<int:board_pk>/columns/<int:column_pk>/', ColumnDetailView.as_view(), name='board-columns-detail'),

    path('columns/<int:column_pk>/tasks/', TaskListView.as_view(), name='column-tasks'),
    path('columns/<int:column_pk>/tasks/<int:task_pk>/', TaskDetailView.as_view(), name='column-task-detail'),

    path('tasks/<int:task_pk>/comments/', CommentListView.as_view(), name='task-comments'),
    path('tasks/<int:task_pk>/comments/<int:comment_pk>/', CommentDetailView.as_view(), name='task-comment-detail'),
]
