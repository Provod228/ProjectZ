from django.db import transaction
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated



from BoardApp.models import Membership, Board
from BoardApp.permissions import BoardPermission
from BoardApp.serializations import BoardItemSerializer, BoardSerializer


@extend_schema(tags=['boards'])
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
