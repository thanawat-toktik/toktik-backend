from django.urls import path

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('', views.VideoViewSet)

urlpatterns = [
    path("update-db/", views.PutVideoInDB.as_view(), name="Update DB"),
    path(
        "upload-psurl/",
        views.UploadPresignedURLView.as_view(),
        name="Generate Pre-signed URL",
    ),
    path("check-queue/", views.UpdateProcessedVideoInDBView.as_view(), name="Check Queue"),
    path("get-url/", views.GetPresignedURLView.as_view(), name="Get presigned url"),
]
urlpatterns += router.urls
