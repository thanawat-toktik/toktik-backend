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
        name="Generate Pre-signed URL",
    ),
    path("get-url/", views.GetPresignedURLView.as_view(), name="Get presigned url"),

    path("update-db/", workers.PutVideoInDB.as_view(), name="Update DB"),
    path("check-queue/", workers.UpdateProcessedVideoInDBView.as_view(), name="Check Queue"),
]
urlpatterns += router.urls
