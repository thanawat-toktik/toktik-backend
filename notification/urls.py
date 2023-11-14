from django.urls import path

from .views import FetchNotifications, UpdateSeen

urlpatterns = [
    path("fetch/", FetchNotifications.as_view(), name="Fetch notifications"),
    path("update-seen/", UpdateSeen.as_view(), name="Update seen"),
]
