from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from BoardApp.models import Task, Comment
from BoardApp.permissions import BoardPermission
from BoardApp.serializations import CommentSerializer


# Create your views here.


@extend_schema(tags=['comments'])
class CommentListView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, BoardPermission]

    def get_task(self):
        task = get_object_or_404(
            Task.objects.select_related('column__board'),
            pk=self.kwargs['task_pk'],
            column__board__membership__user=self.request.user,
        )
        self.check_object_permissions(self.request, task.column.board)
        return task

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Comment.objects.none()
        return Comment.objects.filter(task=self.get_task())

    def create(self, request, *args, **kwargs):
        task = self.get_task()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(task=task, author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@extend_schema(tags=['comments'])
class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.none()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, BoardPermission]

    def get_object(self):
        comment = get_object_or_404(
            Comment.objects.select_related('task__column__board'),
            pk=self.kwargs['comment_pk'],
            task_id=self.kwargs['task_pk'],
            task__column__board__membership__user=self.request.user,
        )
        self.check_object_permissions(self.request, comment.task.column.board)
        if self.request.method in ('PUT', 'PATCH') and comment.author_id != self.request.user.pk:
            raise PermissionDenied('Редактировать комментарий может только его автор.')
        return comment

