import os

from celery import Celery
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv

from video.serializers import CreateVideoSerializer, GeneralVideoSerializer
from video.models import Video

BUCKET_NAMES = {
    "raw": os.environ.get("S3_BUCKET_NAME_RAW"),
    "converted": os.environ.get("S3_BUCKET_NAME_CONVERTED"),
    "chunked": os.environ.get("S3_BUCKET_NAME_CHUNKED"),
    "thumbnail": os.environ.get("S3_BUCKET_NAME_THUMBNAIL"),
}

def get_s3_client():
    return boto3.client(
        "s3",
        region_name=os.environ.get("S3_REGION"),
        endpoint_url=os.environ.get("S3_RAW_ENDPOINT"),
        aws_access_key_id=os.environ.get("S3_ACCESS_KEY"),
        aws_secret_access_key=os.environ.get("S3_SECRET_ACCESS_KEY"),
        config=Config(s3={"addressing_style": "virtual"}, signature_version="v4"),
    )


# https://stackoverflow.com/questions/21508982/add-custom-route-to-viewsets-modelviewset
class VideoViewSet(viewsets.ViewSet):
    queryset = Video.objects.all().order_by('-view')  # -view --> descending view
    permission_classes = [IsAuthenticated,]
    serializer_class = GeneralVideoSerializer

    # TODO: add pagination
    @action(detail=False, methods=['GET'])
    def feed(self, request):
        serializer = self.serializer_class(data=self.queryset, many=True)
        serializer.is_valid()  # dont actually need to check if valid
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    # TODO: add pagination
    @action(detail=False, methods=['GET'], url_path='my-video')
    def my_video(self, request):
        user_id = request.user.id
        data = self.queryset.filter(uploader_id=user_id).order_by('-upload_timestamp')
        serializer = self.serializer_class(data=data, many=True)
        serializer.is_valid()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['PATCH'], url_path='view')
    def increment_view(self, request):
        return Response(data={"message": "View Increment not yet implemented"}, status=status.HTTP_200_OK)


class GetPresignedURLView(GenericAPIView):
    queryset = Video.objects.all()

    def post(self, request):
        print(request.data)
        # payload validation
        target_bucket = request.data.get('bucket', None)
        ids = request.data.get('video_ids')
        if not target_bucket or not ids:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # video id validation
        videos = self.queryset.filter(id__in=ids)
        if not videos: # no match
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        urls = dict()
        try:
            for video in videos:
                url = get_s3_client().generate_presigned_url(
                    ClientMethod='get_object',
                    Params={
                        'Bucket': target_bucket,
                        'Key': video.s3_key
                    },
                    ExpiresIn=300
                )
                urls[video.id] = url
            
            return Response(data=urls, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(e)
            return Response(data={'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UploadPresignedURLView(GenericAPIView):
    permission_classes = [
        # IsAuthenticated,
    ]

    def post(self, request):
        load_dotenv()
        try:
            return Response(
                data={
                    "url": get_s3_client().generate_presigned_url(
                        ClientMethod="put_object",
                        Params={
                            "Bucket": os.environ.get("S3_BUCKET_NAME_RAW"),
                            "Key": request.data["key"],
                        },
                        ExpiresIn=300,
                    )
                },
                status=status.HTTP_200_OK,
            )
        except ClientError as e:
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


def get_celery_app():
    internal_app = Celery("converter",
                          broker=f"redis://"
                                 f"{os.environ.get('REDIS_HOSTNAME', 'localhost')}"
                                 f":{os.environ.get('REDIS_PORT', '6381')}",
                          backend=f"redis://"
                                  f"{os.environ.get('REDIS_HOSTNAME', 'localhost')}"
                                  f":{os.environ.get('REDIS_PORT', '6381')}",
                          broker_connection_retry_on_startup=True)
    return internal_app


def enqueue_conversion(object_name: str):
    load_dotenv()
    identifier, _ = os.path.splitext(object_name)
    celery = get_celery_app()
    celery.send_task("toktik_converter.tasks.do_conversion", args=(object_name,), task_id=identifier)
    return None


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
            enqueue_conversion(data["s3_key"])
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class UpdateProcessedVideoInDBView(GenericAPIView):
    def get(self, _):
        app = get_celery_app()
        unprocessed_videos = Video.objects.filter(isProcessed=False)
        for video in unprocessed_videos:
            task_id, _ = os.path.splitext(video.s3_key)
            async_result = app.AsyncResult(task_id)
            if async_result.ready() and async_result.get():
                video.isProcessed = True
                video.save()
        return Response(status=status.HTTP_200_OK)
