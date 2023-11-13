from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

from video.serializers.like_serializers import CreateLikeSerializer
from notification.views import create_notification
from video.models import Like


class LikeVideo(GenericAPIView):
    serializer_class = CreateLikeSerializer

    # permission_classes = [IsAuthenticated, ]

    def get(self, request):
        user_id = request.user.id
        video_id = request.query_params.get("videoId", None)
        if video_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "videoId not provided"})
        try:
            liked_by = Like.objects.filter(video=video_id, is_liked=True).all()
            return Response(status=status.HTTP_200_OK,
                            data={"isLiked": liked_by.filter(user=user_id).exists(), "likeCount": liked_by.count()})
        except Like.DoesNotExist:
            return Response(status=status.HTTP_200_OK, data={"isLiked": False})

    def get(self, request):
        user_id = request.user.id
        video_id = request.query_params.get("videoId", None)
        if video_id is None:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"message": "videoId not provided"})
        try:
            liked_by = Like.objects.filter(video=video_id, is_liked=True).all()
            return Response(status=status.HTTP_200_OK,
                            data={"isLiked": liked_by.filter(user=user_id).exists(), "likeCount": liked_by.count()})
        except Like.DoesNotExist:
            return Response(status=status.HTTP_200_OK, data={"isLiked": False})

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.set_user(request.user)
            print(serializer)
            serializer.save()
            create_notification("like", request.user, serializer.data.get("video_id"))
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
