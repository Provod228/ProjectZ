from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Board, Column, Comment, Membership, Task
from .permissions import BoardPermission
from .serializations import (
    BoardItemSerializer, BoardSerializer, ColumnSerializer, CommentSerializer,
    TaskSerializer, TaskUpdateSerializer,
)


# Create your views here.




class BoardModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, BoardPermission]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BoardItemSerializer
        return BoardSerializer

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Board.objects.none()
        queryset = Board.objects.filter(
            membership__user=self.request.user,
        )

        if self.action == 'retrieve':
            queryset = queryset.prefetch_related('columns__tasks')

        return queryset

    @transaction.atomic
    def perform_create(self, serializer):
        board = serializer.save()

        Membership.objects.create(
            user=self.request.user,
            board=board,
            role=Membership.Role.OWNER,
        )



class ColumnListView(APIView):
    serializer_class = ColumnSerializer
    permission_classes = [IsAuthenticated, BoardPermission]

    def get_board(self, request, board_pk):
        board = get_object_or_404(
            Board, pk=board_pk, membership__user=request.user,
        )
        self.check_object_permissions(request, board)
        return board

    def get(self, request, board_pk) -> Response:
        board = self.get_board(request, board_pk)
        columns = Column.objects.filter(board=board)
        serializer = self.serializer_class(columns, many=True)
        return Response(serializer.data)

    def post(self, request, board_pk):
        board = self.get_board(request, board_pk)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(board=board)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ColumnDetailView(APIView):
    serializer_class = ColumnSerializer
    permission_classes = [IsAuthenticated, BoardPermission]

    def get_column(self, request, board_pk, column_pk):
        column = get_object_or_404(
            Column.objects.select_related('board'),
            pk=column_pk,
            board_id=board_pk,
            board__membership__user=request.user,
        )
        self.check_object_permissions(request, column.board)

        return column

    def patch(self, request, board_pk, column_pk) -> Response:
        columns = self.get_column(request, board_pk, column_pk)
        serializer = self.serializer_class(columns, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, board_pk, column_pk) -> Response:
        columns = self.get_column(request, board_pk, column_pk)
        serializer = self.serializer_class(columns, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, board_pk, column_pk) -> Response:
        columns = self.get_column(request, board_pk, column_pk)
        columns.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TaskListView(APIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated, BoardPermission]

    def get_column(self, request, column_pk):
        column = get_object_or_404(
            Column.objects.select_related('board'),
            pk=column_pk, board__membership__user=request.user,
        )
        self.check_object_permissions(request, column.board)
        return column

    def get(self, request, column_pk) -> Response:
        column = self.get_column(request, column_pk)
        tasks = Task.objects.filter(column=column)
        serializer = self.serializer_class(tasks, many=True)
        return Response(serializer.data)


    def post(self, request, column_pk):
        column = self.get_column(request, column_pk)
        serializer = self.serializer_class(data=request.data, context={'column': column})
        serializer.is_valid(raise_exception=True)
        serializer.save(column=column)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TaskDetailView(APIView):
    serializer_class = TaskUpdateSerializer
    permission_classes = [IsAuthenticated, BoardPermission]

    def get_task(self, request, column_pk, task_pk):
        task = get_object_or_404(
            Task.objects.select_related('column__board').select_for_update(of=('self',)),
            pk=task_pk,
            column_id=column_pk,
            column__board__membership__user=request.user,
        )
        self.check_object_permissions(request, task.column.board)

        return task

    @transaction.atomic
    def patch(self, request, column_pk, task_pk) -> Response:
        task = self.get_task(request, column_pk, task_pk)
        serializer = self.serializer_class(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def put(self, request, column_pk, task_pk) -> Response:
        task = self.get_task(request, column_pk, task_pk)
        serializer = self.serializer_class(task, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @transaction.atomic
    def delete(self, request, column_pk, task_pk) -> Response:
        task = self.get_task(request, column_pk, task_pk)
        task.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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

