from django.urls import path

from rest_framework.routers import DefaultRouter

from . import views
from . import workers

router = DefaultRouter()
router.register('', views.VideoViewSet)

urlpatterns = [
    path(
        "upload-psurl/",
        views.UploadPresignedURLView.as_view(),
        name="Generate upload pre-signed URL",
    ),
    path("get-url/", views.GetPresignedURLView.as_view(), name="Generate view pre-signed url"),
    path("get-playlist/", views.GetPresignedPlaylistView.as_view(), name="Generate playlist pre-signed url"),

    path("update-db/", workers.PutVideoInDB.as_view(), name="Update DB"),
]
urlpatterns += router.urls
