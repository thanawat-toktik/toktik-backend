from django.forms import ValidationError
from rest_framework import status
from rest_framework import serializers

from authentication.serializers import BasicUserInfoSerializer
from video.serializers.video_serializers import BasicVideoSerializer
from video.models import Comment, Video


class GeneralCommentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    user = BasicUserInfoSerializer(read_only=True, many=False)
    video = BasicVideoSerializer(read_only=True, many=False)
    created_at = serializers.DateTimeField()
    content = serializers.CharField(max_length=200, allow_blank=False)

    class Meta:
        model = Comment
        fields = ["id", "user", "video", "created_at", "content",]

class CreateCommentSerializer(serializers.Serializer):
    content = serializers.CharField(max_length=200, allow_blank=False)
    video_id = serializers.IntegerField()

    class Meta:
        fields = ["content", "video_id"]
    
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
        new_comment = Comment(**validated_data)
        new_comment.user = self.user
        new_comment.save()
        return new_comment
    