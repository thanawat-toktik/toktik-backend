from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from utils.redis_util import publish_message_to_wss

from video.models import Comment
from video.serializers.comment_serializers import CreateCommentSerializer
from notification.views import create_notification


class CommentView(GenericAPIView):
    serializer_class = CreateCommentSerializer
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        video_id = request.query_params.get("video_id", None)
        if not video_id:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "video_id not provided"})

        comments = Comment.objects.filter(video_id=video_id).all()
        formed_comments = [{"user": comment.user.username, "content": comment.content}
                           for comment in comments]
        return Response(status=status.HTTP_200_OK, data=formed_comments)

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.set_user(request.user)
            serializer.save()
            create_notification("comment", request.user, serializer.data.get("video_id"))

            comment_payload = {
                "user": request.user.username,
                "user_id": request.user.id,
                "content": serializer.data.get("content"),
                "video_id": serializer.data.get("video_id"),
            }
            publish_message_to_wss("WSS-comment", comment_payload)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
