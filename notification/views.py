from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
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
    for user_id in involved_users:
        Notification.objects.create(
            notification_type=notification_type,
            sender_id=sender.id,
            receiver_id=user_id,
            video_id=video_id,
            timestamp=timestamp,
        ).save()

    # generate notif payload for WS server
    payload = {
        "timestamp": timestamp,
        "video_id": video_id,
        "message": generate_notification_message(sender.username, notification_type, video.title),
        "sender": sender.id,
        "receivers": involved_users,
    }
    # send the payload
    publish_message_to_wss("WSS-notif", payload)


class FetchNotifications(GenericAPIView):
    permission_classes = [IsAuthenticated]

    @method_decorator(cache_page(5))
    def get(self, request):
        user_id = request.user.id
        notifications = Notification.objects.filter(receiver_id=user_id).order_by("-timestamp")[:5]
        notifications = [{
            "message": generate_notification_message(notif.sender, notif.notification_type, notif.video.title),
            "timestamp": notif.timestamp,
        } for notif in notifications]
        return Response(status=status.HTTP_200_OK, data=notifications)
