from django.urls import path

from .views import FetchNotifications

urlpatterns = [
    path("fetch/", FetchNotifications.as_view(), name="Fetch notifications"),
]
