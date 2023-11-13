from notification.models import NOTIFICATION_MESSAGE

def generate_notification_message(username, notification_type, video_title):
    action = NOTIFICATION_MESSAGE.get(notification_type, None)
    if not action:
        raise ValueError("Invalid notification type")
    return f"{username} {action} \"{video_title}\""
