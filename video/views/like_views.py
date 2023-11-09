from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

from video.serializers.like_serializers import CreateLikeSerializer
from video.models import Like


class LikeVideo(GenericAPIView):
    serializer_class = CreateLikeSerializer
    permission_classes = [IsAuthenticated, ]

    def get(self, request):
        user_id = request.user.id
        video_id = request.query_params.get("videoId", None)
        if video_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "videoId not provided"})
        try:
            like_entry = Like.objects.get(user=user_id, video=video_id)
            return Response(status=status.HTTP_200_OK, data={"isLiked": like_entry.isLiked})
        except Like.DoesNotExist:
            return Response(status=status.HTTP_200_OK, data={"isLiked": False})

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.set_user(request.user)
            serializer.save()
            # TODO: should send notification here
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
