from django.forms import ValidationError
from rest_framework import status
from rest_framework import serializers

from video.models import Like
from video.models import Video

class CreateLikeSerializer(serializers.Serializer):
    video_id = serializers.IntegerField()

    class Meta:
        fields = ["video_id"]

    def validate(self, attrs):
        video = Video.objects.get(id=attrs.get("video_id"))
        if not video:
            raise ValidationError(
                message="Video does not exist",
                code=status.HTTP_403_FORBIDDEN,
            )

        return super().validate(attrs)
    
    def set_user(self, user):
        self.user = user

    def create(self, validated_data):
        obj, created = Like.objects.get_or_create(
            user=self.user,
            video_id=validated_data.get("video_id"),
            defaults={"is_liked": True}
        )
        if not created:
            obj.is_liked = not obj.is_liked
        
        obj.save()
        return obj
