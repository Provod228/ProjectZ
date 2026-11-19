from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from BoardApp.models import Board, Column
from BoardApp.permissions import BoardPermission
from BoardApp.serializations import ColumnSerializer


@extend_schema(tags=['columns'])
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


@extend_schema(tags=['columns'])
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
