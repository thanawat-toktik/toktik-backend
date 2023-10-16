from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated

class TestView(GenericAPIView):
    # add this to the endpoints that requires authen
    permission_classes = [IsAuthenticated, ] 

    def get(self, request):
        
        return Response(
            data={'hello': 'world'},
            status=status.HTTP_200_OK
        )
