from django.urls import path

from . import views

urlpatterns = [
    path("test/", views.TestView.as_view(), name="temp function"),
    path("update-db/", views.PutVideoInDB.as_view(), name="Update DB"),
    path(
        "upload-psurl/",
        views.UploadPresignedURLView.as_view(),
        name="Generate Pre-signed URL",
    ),
]
