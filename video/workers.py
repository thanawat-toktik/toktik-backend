import os

from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from celery import Celery

from dotenv import load_dotenv

from video.serializers import CreateVideoSerializer
from video.models import Video

def get_celery_app(channel_number=0):
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
def update_video(video: Video, task_result: bool, task_id: str):
    step = int(video.isConverted) + int(video.isChunked) + int(video.hasThumbnail)
    if not task_result: # if something fails
        if ("processing" in video.status):
            video.status = "retrying"
            enqueue_task(task_id, step)
        else:
            video.status = "failed"
    else: # successfully performed the previous step
        video.status = "processing"
        if step == 0:
            video.isConverted = True
            enqueue_task(task_id, 1)
        elif step == 1:
            video.isChunked = True
            enqueue_task(task_id, 2)
        else:
            video.hasThumbnail = True
            video.status = "done"
    video.save()

class UpdateProcessedVideoInDBView(GenericAPIView):
    def get(self, _):
        app = get_celery_app()

        # get videos that are not done & not failed
        dispatched_videos = Video.objects.exclude(status__in=["done", "failed"])
        counter = 0
        for video in dispatched_videos:
            if counter > 20:
                break
            # get video info
            task_id, _ = os.path.splitext(video.s3_key)
            async_result = app.AsyncResult(task_id)
            # check status in MQ
            if not async_result.ready():
                continue
            
            update_video(video, async_result.get(), task_id)
            counter += 1
        return Response(status=status.HTTP_200_OK)
