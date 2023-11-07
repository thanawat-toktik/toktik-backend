from rest_framework import serializers

from authentication.serializers import BasicUserInfoSerializer
from video.serializers.video_serializers import BasicVideoSerializer
from video.models import Comment


class GeneralCommentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    user = BasicUserInfoSerializer(read_only=True, many=False)
    video = BasicVideoSerializer(read_only=True, many=False)
    created_at = serializers.DateTimeField()
    content = serializers.CharField(max_length=200, allow_blank=False)

    class Meta:
        model = Comment
        fields = ["id", "user", "video", "created_at", "content",]

class CreateCommentSerializer(serializers.ModelSerializer):
    content = serializers.CharField(max_length=200, allow_blank=False)
    video_id = serializers.IntegerField(source="video.id") # TODO: need testing

    class Meta:
        model = Comment
        fields = ["content", "video_id"]

    def set_user(self, user):
        self.user = user

    def create(self, validated_data):
        new_comment = Comment(**validated_data)
        new_comment.user = self.user
        new_comment.video = self.video_id
        new_comment.save()
        return new_comment
    