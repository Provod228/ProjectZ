
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Board
from .serializations import BoardSerializer


# Create your views here.




class BoardModelViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]