from django.forms import ValidationError
from rest_framework import status
from rest_framework import serializers
from authentication.serializers import BasicUserInfoSerializer

from video.models import Video
from rest_framework import serializers


class GeneralVideoSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    uploader = BasicUserInfoSerializer(read_only=True, many=False)
    upload_timestamp = serializers.DateTimeField()
    title = serializers.CharField(max_length=50, allow_blank=False)
    caption = serializers.CharField(max_length=100, allow_blank=True)
    view = serializers.IntegerField()
    isConverted = serializers.BooleanField()
    isChunked = serializers.BooleanField()
    hasThumbnail = serializers.BooleanField()

    class Meta:
        model = Video
        fields = ['id', 'uploader', 'upload_timestamp', 'title', 'caption', 'view', 'isConverted', 'isChunked', 'hasThumbnail']


class CreateVideoSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=50, allow_blank=False)
    caption = serializers.CharField(max_length=100, allow_blank=True)
    s3_key = serializers.CharField(max_length=45, allow_blank=False)

    class Meta:
        model = Video
        fields = ["s3_key", "title", "caption"]

    def validate(self, attrs):
        s3_key = Video.objects.filter(s3_key=attrs.get("s3_key")).exists()
        if s3_key:
            raise ValidationError(
                message="Video does not have S3 key to its object!",
                code=status.HTTP_403_FORBIDDEN,
            )

        return super().validate(attrs)

    def set_user(self, user):
        self.uploader = user

    def create(self, validated_data):
        new_video = Video(**validated_data)
        new_video.uploader = self.uploader
        new_video.save()
        return new_video
