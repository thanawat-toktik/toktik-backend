from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

from video.serializers.comment_serializers import CreateCommentSerializer
from notification.views import create_notification

class PostComment(GenericAPIView):
    serializer_class = CreateCommentSerializer
    permission_classes = [IsAuthenticated,]

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.set_user(request.user)
            serializer.save()
            create_notification("comment", request.user, serializer.video_id)
            # TODO: send comment update to FE through WSS
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
