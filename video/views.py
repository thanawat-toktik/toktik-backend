import os

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
from dotenv import load_dotenv

from video.serializers import GeneralVideoSerializer
from video.models import Video

BUCKET_NAMES = {
    "raw": os.environ.get("S3_BUCKET_NAME_RAW"),
    "converted": os.environ.get("S3_BUCKET_NAME_CONVERTED"),
    "chunked": os.environ.get("S3_BUCKET_NAME_CHUNKED"),
    "thumbnail": os.environ.get("S3_BUCKET_NAME_THUMBNAIL"),
}
FILE_EXTENSION = {
    "converted": ".mp4",
    "chunked": ".m3u8",
    "thumbnail": ".jpg"
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
    queryset = Video.objects.all()  # -view --> descending view
    # permission_classes = [IsAuthenticated,]
    serializer_class = GeneralVideoSerializer

    # TODO: add pagination
    @action(detail=False, methods=['GET'])
    def feed(self, request):
        # data = self.queryset.filter(status='done').order_by('-view')
        data = self.queryset.filter(status='done').order_by('-view')
        serializer = self.serializer_class(data=data, many=True)
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
        # payload validation
        target_bucket = request.data.get('bucket', None)
        ids = request.data.get('video_ids').split(',')
        if not target_bucket or not ids:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # video id validation
        videos = self.queryset.filter(id__in=ids)  # currently, the ids are str, but it works
        if not videos:  # no match
            return Response(status=status.HTTP_404_NOT_FOUND)

        urls = {
            "video_ids": [],
            "urls": []
        }
        try:
            for video in videos:
                identifier, original_ext = os.path.splitext(video.s3_key)
                url = get_s3_client().generate_presigned_url(
                    ClientMethod='get_object',
                    Params={
                        'Bucket': BUCKET_NAMES.get(target_bucket),
                        'Key': identifier + FILE_EXTENSION.get(target_bucket, f".{original_ext}")
                    },
                    ExpiresIn=300
                )
                urls["video_ids"].append(video.id)
                urls["urls"].append(url)

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

