from django.forms import ValidationError
from rest_framework import status
from rest_framework import serializers

from video.models import Video
from django.contrib.auth.models import User
from rest_framework import serializers


class GeneralVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(GeneralVideoSerializer, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False
    

class CreateVideoSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=50, allow_blank=False)
    caption = serializers.CharField(max_length=100, allow_blank=True)
    s3_key = serializers.CharField(max_length=45, allow_blank=False)

    # created_at = serializers.DateTimeField(read_only=True)
    # upload_timestamp = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Video
        fields = ["s3_key", "title", "caption"]

    def validate(self, attrs):
        title = Video.objects.filter(title=attrs.get("title")).exists()
        if title:
            raise ValidationError(
                detail="Video does not have title!", code=status.HTTP_403_FORBIDDEN
            )

        s3_key = Video.objects.filter(s3_key=attrs.get("s3_key")).exists()
        if s3_key:
            raise ValidationError(
                detail="Video does not have S3 key to its object!",
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
