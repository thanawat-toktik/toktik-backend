from django.forms import ValidationError
from rest_framework import status
from rest_framework import serializers

from video.models import Video


class CreateVideoSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=50, allow_blank=False)
    caption = serializers.CharField(max_length=100, allow_blank=True)
    s3_key = serializers.CharField(max_length=36, allow_blank=False)

    created_at = serializers.DateTimeField(read_only=True)
    upload_timestamp = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Video
        fields = ["id", "created_at", "upload_timestamp", "s3_key", "title", "caption"]

    def validate(self, attrs):
        title = Video.objects.filter(title=attrs.get("title")).exists()
        if title:
            raise ValidationError(
                detail="Video does not have title!", code=status.HTTP_403_FORBIDDEN
            )

        caption = Video.objects.filter(caption=attrs.get("caption")).exists()
        if caption:
            raise ValidationError(
                detail="Video does not have caption!", code=status.HTTP_403_FORBIDDEN
            )

        s3_key = Video.objects.filter(s3_key=attrs.get("s3_key")).exists()
        if s3_key:
            raise ValidationError(
                detail="Video does not have S3 key to its object!",
                code=status.HTTP_403_FORBIDDEN,
            )

        return super().validate(attrs)

    def create(self, validated_data):
        new_video = Video(**validated_data)
        new_video.save()
        return new_video
