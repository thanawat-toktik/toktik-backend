from rest_framework import serializers

from video.models import Like


class CreateLikeSerializer(serializers.ModelSerializer):
    video_id = serializers.IntegerField(source="video.id") # TODO: need testing

    class Meta:
        model = Like
        fields = ["video", "isLiked"]

    def set_user(self, user):
        self.user = user

    def create(self, validated_data):
        new_comment = Like(**validated_data)
        new_comment.user = self.user
        new_comment.video = self.video_id
        new_comment.save()
        return new_comment
    