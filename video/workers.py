import os

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from celery import Celery

from dotenv import load_dotenv

from video.serializers import CreateVideoSerializer
from video.models import Video


def get_celery_app(channel_number: int):
    internal_app = Celery("converter",
                          broker=f"redis://"
                                 f"{os.environ.get('REDIS_HOSTNAME', 'localhost')}"
                                 f":{os.environ.get('REDIS_PORT', '6381')}"
                                 f"/{channel_number}",
                          backend=f"redis://"
                                  f"{os.environ.get('REDIS_HOSTNAME', 'localhost')}"
                                  f":{os.environ.get('REDIS_PORT', '6381')}"
                                  f"/{channel_number}",
                          broker_connection_retry_on_startup=True)
    return internal_app


TASKS = {
    0: "toktik_converter.tasks.do_conversion",
    1: "toktik_chunker.tasks.do_chunking",
    2: "toktik_thumbnailer.tasks.extract_thumbnail",
}


def enqueue_task(object_name: str, channel: int):
    load_dotenv()
    identifier, _ = os.path.splitext(object_name)
    celery = get_celery_app(channel)
    celery.send_task(TASKS.get(channel), args=(object_name,), task_id=identifier)
    print(f"SENT TASK WITH ID: [{identifier}]")
    print(f"SENT TO CHANNEL: [{channel}]")
    return None


# step 1
# (triggered by receiving request from frontend)
# - put info of received raw video into DB
# - also sends a message to msg queue to convert it
class PutVideoInDB(GenericAPIView):
    queryset = Video.objects.all()
    serializer_class = CreateVideoSerializer

    permission_classes = [
        # IsAuthenticated,
    ]

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)

        if serializer.is_valid():
            serializer.set_user(request.user)
            serializer.save()
            enqueue_task(data["s3_key"], 0)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# step 2
# (triggered by scheduler)
# - sets flags to true according to status
# - sends a message to msg queue
def update_video(video: Video, task_result: bool, step: int):
    # print("before")
    # print(step)
    # print(task_result)
    # print(video.__dict__)

    if not task_result:  # if something fails
        if ("processing" in video.status):
            video.status = "retrying"
            enqueue_task(video.s3_key, step)
        else:
            video.status = "failed"
    else:  # successfully performed the previous step
        video.status = "processing"
        if step == 0:
            video.isConverted = True
            enqueue_task(video.s3_key, 1)
        elif step == 1:
            video.isChunked = True
            enqueue_task(video.s3_key, 2)
        else:
            video.hasThumbnail = True
            video.status = "done"
    video.save()

    # print("after")
    # print(video.__dict__)


class UpdateProcessedVideoInDBView(GenericAPIView):
    def get(self, _):
        # get videos that are not done & not failed
        dispatched_videos = Video.objects.exclude(status__in=["done", "failed"])[:20]
        for video in dispatched_videos:
            # check state of the video
            step = int(video.isConverted) + int(video.isChunked) + int(video.hasThumbnail)
            # get video info
            task_id, _ = os.path.splitext(video.s3_key)
            async_result = get_celery_app(step).AsyncResult(task_id)
            # check status in MQ
            if not async_result.ready():
                continue

            update_video(video, async_result.get(), step)
        return Response(status=status.HTTP_200_OK)
