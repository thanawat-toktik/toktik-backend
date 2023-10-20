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

from video.serializers import CreateVideoSerializer, GeneralVideoSerializer
from video.models import Video


# https://stackoverflow.com/questions/21508982/add-custom-route-to-viewsets-modelviewset
class VideoViewSet(viewsets.ViewSet):
    queryset = Video.objects.all().order_by('-view') # -view --> descending view
    permission_classes = []
    serializer_class = GeneralVideoSerializer

    #TODO: add pagination
    @action(detail=False, methods=['GET'])
    def feed(self, request):
        serializer = self.serializer_class(data=self.queryset, many=True)
        serializer.is_valid() # dont actually need to check if valid
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
    
    #TODO: add pagination
    @action(detail=False, methods=['GET'], url_path='my-video')
    def my_video(self, request):
        user_id = request.user.id
        data = self.queryset.filter(uploader_id=user_id).order_by('-upload_timestamp')
        serializer = self.serializer_class(data=data, many=True)
        serializer.is_valid()
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)
    

    @action(detail=True, methods=['GET'], url_path='')
    def get_presigned(self, request, pk=None):
        
        if not pk:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        video = self.queryset.get(id=pk)
        if not video:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        s3 = boto3.client(
            "s3",
            region_name=os.environ.get("S3_REGION"),
            endpoint_url=os.environ.get("S3_RAW_ENDPOINT"),
            aws_access_key_id=os.environ.get("S3_ACCESS_KEY"),
            aws_secret_access_key=os.environ.get("S3_SECRET_ACCESS_KEY"),
            config=Config(s3={"addressing_style": "virtual"}, signature_version="v4"),
        )
        
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': os.environ.get("S3_BUCKET_NAME"),
                'Key': video.s3_key
            },
            ExpiresIn=300
        )
        print(url)

        return Response(data={"presigned_url": url}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'])
    def thumbnails(self, request):
        return Response(data={"message": "Thumbnailer not yet implemented"}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['PATCH'], url_path='view')
    def increment_view(self, request):
        return Response(data={"message": "View Increment not yet implemented"}, status=status.HTTP_200_OK)



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
