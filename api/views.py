from rest_framework import viewsets, filters
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import *


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=False)
    def me(self, request, pk=None):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


# ViewSets define the view behavior.
class UserInfoViewSet(viewsets.ModelViewSet):
    queryset = UserInfo.objects.all()
    serializer_class = UserInfoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['fio']

    @action(detail=False)
    def user(self, request, *args, **kwargs):
        if not 'target_id' in kwargs:
            return Response({"detail": "No data"}, status=400)
        target_user = int(kwargs['target_id'])
        queryset = get_object_or_404(self.queryset, user=target_user)
        serializer = UserInfoSerializer(queryset)
        return Response(serializer.data)
    @action(detail=False, permission_classes=[IsAuthenticated], methods=['POST'])
    def update_info(self, request, *args, **kwargs):
        user = request.user
        queryset = self.queryset.filter(user=user)
        for i in queryset:
            queryset.delete()
        serializer = UserInfoSerializer(data=request.data)
        if serializer.is_valid():
            UserInfo.objects.create(user=user,fio=serializer.data['fio'],about=serializer.data['about'],number=serializer.data['number'],avatar=request.FILES['avatar'])
            return Response({'success':True})
        return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([AllowAny])
def comment(request):
    send_mail(
        f'Отзыв о сотруднике {request.data["employer"]} - Antares',
        f'{request.data["text"]}',
        None,
        [u.email for u in User.objects.filter(is_staff=True)],
        fail_silently=False,
    )
    return Response({"success": True})


@api_view(['GET'])
@permission_classes([AllowAny])
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return Response(ip)
