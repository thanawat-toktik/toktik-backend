from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

from video.serializers.like_serializers import CreateLikeSerializer
from notification.models import Notification
from notification.views import create_notification
from utils.redis_util import publish_message_to_wss

class LikeVideo(GenericAPIView):
    serializer_class = CreateLikeSerializer
    # permission_classes = [IsAuthenticated, ]

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.set_user(request.user)
            serializer.save()
            create_notification("like", request.user, serializer.video_id)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
