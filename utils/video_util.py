from video.models import Video


# if a user likes a video, notification should only appear for video owner
def handle_like_notif(video_id) -> (list[int], Video):
    video = Video.objects.get(id=video_id)
    if not video:
        return [], None
    else:
        return [video.uploader.id], video


# if a user comments on a video, notification should appear for the video owner and people who recently commented
def handle_comment_notif(video_id) -> (list[int], Video):
    video = Video.objects.prefetch_related('comments').get(id=video_id)
    if not video:
        return [], None

    user_ids = list(video.comments.values_list('user_id', flat=True).distinct())
    print(user_ids)
    if video.uploader.id not in user_ids:
        user_ids.append(video.uploader.id)

    return user_ids, video


def get_subscribed_user_ids(video_id, notification_type) -> (list[int], Video):
    if notification_type == "like":
        return handle_like_notif(video_id)
    elif notification_type == "comment":
        return handle_comment_notif(video_id)
    else:
        raise ValueError("Invalid notification type")
