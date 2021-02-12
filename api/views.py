from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import UserSerializer, GroupSerializer


# Create your views here.
@permission_classes([IsAuthenticated])
class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


@permission_classes([IsAuthenticated])
class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


@api_view(['POST'])
def comment(request):
    send_mail(
        f'Отзыв о сотруднике {request.data["employer"]} - Antares',
        f'{request.data["text"]}',
        None,
        [u.email for u in User.objects.filter(is_staff=True)],
        fail_silently=False,
    )
    return Response({"success": True})
