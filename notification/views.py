from django.utils import timezone
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from authentication.models import User

from notification.models import Notification
from utils.notification_util import generate_notification_message
from utils.redis_util import publish_message_to_wss
from utils.video_util import get_subscribed_user_ids


def create_notification(notification_type: str, sender: User, video_id: int):
    involved_users, video = get_subscribed_user_ids(video_id, notification_type)
    timestamp = timezone.now().isoformat()

    # store them in DB for each receiver
    new_notification_ids = []
    for user_id in involved_users:
        new_notification = Notification.objects.create(
            notification_type=notification_type,
            sender_id=sender.id,
            receiver_id=user_id,
            video_id=video_id,
            timestamp=timestamp,
        )
        new_notification.save()
        new_notification_ids.append(new_notification.id)

    # generate notif payload for WS server
    payload = {
        "timestamp": timestamp,
        "video_id": video_id,
        "message": generate_notification_message(sender.username, notification_type, video.title),
        "sender": sender.id,
        "receivers": involved_users,
        "notification_ids": new_notification_ids,
    }
    # send the payload
    publish_message_to_wss("WSS-notif", payload)


class FetchNotifications(GenericAPIView):
    permission_classes = [IsAuthenticated]

    # doesn't need caching since only fetched when user logs in
    def get(self, request):
        user_id = request.user.id
        notifications = Notification.objects.filter(receiver_id=user_id).order_by("-timestamp")[:5]
        # notifications = Notification.objects.filter(receiver_id=user_id).order_by("-timestamp")
        notifications = [{
            "notifId": notif.id,
            "message": generate_notification_message(notif.sender, notif.notification_type, notif.video.title),
            "timestamp": notif.timestamp,
            "isSeen": notif.is_seen,
        } for notif in notifications]
        return Response(status=status.HTTP_200_OK, data=notifications)


class UpdateSeen(GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        notification_ids = request.data.get("notification_ids", None)
        if not notification_ids:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        seen_notifications = Notification.objects.filter(id__in=notification_ids)
        for notif in seen_notifications:
            notif.is_seen = True
            notif.save()

        return Response(status=status.HTTP_201_CREATED)
