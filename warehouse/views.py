from rest_framework import viewsets
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from .serializers import *
from .models import *


class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer


class LogViewSet(viewsets.ModelViewSet):
    queryset = Log.objects.all()
    serializer_class = LogSerializer

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], serializer_class=TextSerializer)
    def log_action(self, request):
        user = request.user
        serializer = TextSerializer(data=request.data)
        if serializer.is_valid():
            Log.objects.create(user=user, text=serializer.data['text'])
            return Response({"seccess": True})
        return Response(serializer.errors, status=400)
