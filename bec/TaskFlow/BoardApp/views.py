from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, authentication, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Board, Column, Task, Membership
from .permissions import BoardPermission
from .serializations import BoardSerializer, ColumnSerializer, TaskSerializer, BoardItemSerializer


# Create your views here.




class BoardModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, BoardPermission]

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return BoardItemSerializer
        return BoardSerializer

    def get_queryset(self):
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
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(column=column)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


