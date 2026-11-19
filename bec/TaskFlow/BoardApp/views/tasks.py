from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from BoardApp.models import Column, Task
from BoardApp.permissions import BoardPermission
from BoardApp.serializations import TaskSerializer, TaskUpdateSerializer


@extend_schema(tags=['tasks'])
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


@extend_schema(tags=['tasks'])
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