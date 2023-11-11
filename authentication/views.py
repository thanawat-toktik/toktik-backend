from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework_simplejwt.views import TokenObtainPairView

from authentication.serializers import CreateUserSerializer
from authentication.serializers import CustomObtainTokenSerializer

UserModel = get_user_model()


class UserCreateView(GenericAPIView):
    queryset = UserModel.objects.all()
    serializer_class = CreateUserSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)

        try:
            serializer.is_valid()
            serializer.save()
            return Response(
                data=serializer.data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                data={'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class CustomObtainTokenPairView(TokenObtainPairView):
    serializer_class = CustomObtainTokenSerializer
