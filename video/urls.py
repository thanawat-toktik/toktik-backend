from django.urls import path

from rest_framework.routers import DefaultRouter

from .views import video_views as video
from .views import workers_views as worker
from .views import presigned_url_views as psu
from .views import comment_views as comment
from .views import like_views as like

urlpatterns = []

router = DefaultRouter()
router.register('', video.VideoViewSet)

urlpatterns += router.urls
urlpatterns += [
    path("get-counts/", video.GetVideoStatistics.as_view(), name="Get Statistics"),

    path("update-db/", worker.PutVideoInDB.as_view(), name="Update DB"),
    path("check-queue/", worker.UpdateProcessedVideoInDBView.as_view(), name="Check Queue"),

    path(
        "upload-psurl/",
        psu.UploadPresignedURLView.as_view(),
        name="Generate upload pre-signed URL",
    ),
    path("get-url/", psu.GetPresignedURLView.as_view(), name="Generate view pre-signed url"),
    path("get-playlist/", psu.GetPresignedPlaylistView.as_view(), name="Generate playlist pre-signed url"),

    path("comment/", comment.CommentView.as_view(), name="Comments"),

    path("like/", like.LikeView.as_view(), name="Like Video"),
]
