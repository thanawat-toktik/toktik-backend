from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from video.serializers.video_serializers import GeneralVideoSerializer
from video.models import Video


# https://stackoverflow.com/questions/21508982/add-custom-route-to-viewsets-modelviewset
class VideoViewSet(viewsets.ViewSet):
    queryset = Video.objects.all()
    permission_classes = [IsAuthenticated, ]
    serializer_class = GeneralVideoSerializer

    @action(detail=False, methods=["GET"])
    def feed(self, _):
        data = self.queryset.filter(status="done").order_by("-view")
        serializer = self.serializer_class(data=data, many=True)
        serializer.is_valid()  # dont actually need to check if valid
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["GET"], url_path="my-video")
    def my_video(self, request):
        user_id = request.user.id
        data = self.queryset.filter(uploader_id=user_id).order_by("-upload_timestamp")
        serializer = self.serializer_class(data=data, many=True)
        serializer.is_valid()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["GET"], url_path="view")
    def increment_view(self, _, pk=None):
        video = self.queryset.get(id=pk)
        video.view += 1
        video.save()
        return Response(status=status.HTTP_200_OK)


class GetVideoStatistics(GenericAPIView):
    # https://stackoverflow.com/questions/31237042/whats-the-difference-between-select-related-and-prefetch-related-in-django-orm
    queryset = Video.objects.prefetch_related('comments', 'likes').all()  # this will pre-join the tables
    permission_classes = [IsAuthenticated, ]

    @method_decorator(cache_page(5))
    def get(self, request: Request):
        # payload validation
        ids = request.query_params.get("video_ids", None).split(",")
        ids = [int(vid_id) for vid_id in ids]
        if not ids:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if isinstance(ids, str):
            ids = ids.split(',')

        # video id validation
        videos = self.queryset.filter(id__in=ids)  # currently, the ids are str, but it works
        if not videos:  # no match
            return Response(status=status.HTTP_404_NOT_FOUND)

        id_stats_map = dict()  # { id: { statistic dict } }
        try:
            for video in videos:
                liked_by = video.likes.filter(is_liked=True)
                you_liked = liked_by.filter(user=request.user)
                statistics = {
                    "views": video.view,
                    "likes": liked_by.count(),
                    "comment": video.comments.all().count(),
                    "isLiked": you_liked.exists() and you_liked.first().is_liked,
                }

                id_stats_map[video.id] = statistics

            stats = {
                "video_ids": ids,
                "statistics": [id_stats_map.get(int(id), '') for id in ids]
            }
            return Response(data=stats, status=status.HTTP_200_OK)

        except Exception as e:
            print(e)
            return Response(data={'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
