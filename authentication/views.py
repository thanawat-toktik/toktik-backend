from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView

from authentication.serializers import CreateUserSerializer

UserModel = get_user_model()
class UserCreateView(GenericAPIView):
    queryset = UserModel.objects.all()
    serializer_class = CreateUserSerializer

    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(
                data = serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                data = serializer.error,
                status=status.HTTP_400_BAD_REQUEST
            )

# class UserViewSet(ModelViewSet):
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

#     def list(self, request):
#         serializer = ItemSerializer(self.queryset, many=True)
#         return Response(serializer.data)

#     def retrieve(self, request, pk=None):
#         item = get_object_or_404(self.queryset, pk=pk)
#         serializer = ItemSerializer(item)
#         return Response(serializer.data)

#     @action(detail=False, methods=['get'])
#     def items_not_done(self, request):
#         user_count = Item.objects.filter(done=False).count()

#         return Response(user_count)
