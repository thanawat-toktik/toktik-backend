from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv

from video.serializers import CreateVideoSerializer
from video.models import Video


class TestView(GenericAPIView):
    # add this to the endpoints that requires authen
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        return Response(data={"hello": "world"}, status=status.HTTP_200_OK)


# https://stackoverflow.com/questions/21508982/add-custom-route-to-viewsets-modelviewset
class VideoViewSet(viewsets.ViewSet):
    # -view --> descending view
    queryset = Video.objects.order_by('-view')
    permission_classes = [
        # IsAuthenticated,
    ]

    @action(detail=False, methods=['GET'])
    def feed(self, request):
        return Response(data={"hello": "world"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path='my-video')
    def my_video(self, request):
        return Response(data={"hello": "world"}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['GET'], url_path='')
    def get_presigned(self, request, pk=None):
        return Response(data={"hello": "world"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'])
    def thumbnails(self, request):
        return Response(data={"hello": "world"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['PATCH'], url_path='view')
    def increment_view(self, request):
        return Response(data={"hello": "world"}, status=status.HTTP_200_OK)



class UploadPresignedURLView(GenericAPIView):
    permission_classes = [
        # IsAuthenticated,
    ]

    def post(self, request):
        load_dotenv()
        s3 = boto3.client(
            "s3",
            region_name=os.environ.get("S3_REGION"),
            endpoint_url=os.environ.get("S3_RAW_ENDPOINT"),
            aws_access_key_id=os.environ.get("S3_ACCESS_KEY"),
            aws_secret_access_key=os.environ.get("S3_SECRET_ACCESS_KEY"),
            config=Config(s3={"addressing_style": "virtual"}, signature_version="v4"),
        )

        try:
            return Response(
                data={
                    "url": s3.generate_presigned_url(
                        ClientMethod="put_object",
                        Params={
                            "Bucket": os.environ.get("S3_BUCKET_NAME"),
                            "Key": request.data["key"],
                        },
                        ExpiresIn=300,
                    )
                },
                status=status.HTTP_200_OK,
            )
        except ClientError as e:
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


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
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
