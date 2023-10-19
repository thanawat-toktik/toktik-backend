from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('', views.VideoViewSet)

urlpatterns = [
    path("test/", views.TestView.as_view(), name="temp function"),
    path("update-db/", views.PutVideoInDB.as_view(), name="Update DB"),
    path(
        "upload-psurl/",
        views.UploadPresignedURLView.as_view(),
        name="Generate Pre-signed URL",
    ),
    path('', include(router.urls)),
]
