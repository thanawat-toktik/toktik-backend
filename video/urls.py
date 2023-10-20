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
]
urlpatterns += router.urls
