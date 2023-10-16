from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv


class TestView(GenericAPIView):
    # add this to the endpoints that requires authen
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        return Response(data={"hello": "world"}, status=status.HTTP_200_OK)


class UploadPresignedURLView(GenericAPIView):
    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request):
        load_dotenv()
        s3 = boto3.client(
            "s3",
            region_name=os.environ.get("S3_REGION"),
            endpoint_url=os.environ.get("S3_RAW_ENDPOINT"),
            aws_access_key_id=os.environ.get("S3_ACCESS_KEY"),
            aws_secret_access_key=os.environ.get("S3_SECRET_ACCESS_KEY"),
            config=Config(s3={"addressing_style": "virtual"}),
        )

        try:
            return Response(
                data={
                    "url": s3.generate_presigned_url(
                        ClientMethod="put_object",
                        Params={
                            "Bucket": os.environ.get("S3_BUCKET_NAME"),
                            "Key": "Super awesome key",
                        },
                    )
                },
                status=status.HTTP_200_OK,
            )
        except ClientError as e:
            return Response(data={"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
