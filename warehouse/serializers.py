from rest_framework import serializers
from .models import *


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class LogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'


class TextSerializer(serializers.Serializer):
    text = serializers.CharField(max_length=2000)


class FileSerializer(serializers.Serializer):
    file = serializers.FileField()
