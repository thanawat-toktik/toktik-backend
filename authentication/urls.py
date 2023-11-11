from django.urls import path
from rest_framework_simplejwt.views import (
    # TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from authentication.views import UserCreateView, CustomObtainTokenPairView

urlpatterns = [
    path('register/', UserCreateView.as_view(), name='register'),
    path('jwt/create/', CustomObtainTokenPairView.as_view(), name='token_obtain_pair'),
    path('jwt/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('jwt/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
