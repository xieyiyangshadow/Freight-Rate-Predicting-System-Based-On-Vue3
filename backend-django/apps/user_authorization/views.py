from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .Serializer import (
    UserSerializer,
    UserLoginSerializer,
    UserRegisterSerializer,
)

# Create your views here.
class UserRegisterView(APIView):
    """ 
    用户注册接口
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        POST /api/auth/register/
        
        请求体：
        {
            ”username": "xxx",
            "email": "xxx@example.com",
            "password": "password123",
            "password2": "password123"
        }
        """
        serializer = UserRegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "注册成功",
                    "user": UserSerializer(user).data,
                    "refresh": str(refresh),
                    # "access": str(refresh.access_token),
                },
                status=status.HTTP_201_CREATED,
            )
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserLoginView(APIView):
    """
    用户登录接口
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        POST /api/auth/login/
        
        请求体：
        {
            "email": "xxx@example.com",
            "password": "password123"
        }
        """
        serializer = UserLoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "message": "登录成功",
                    "user": UserSerializer(user).data,
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                },
                status=status.HTTP_200_OK,
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserRefreshTokenView(APIView):
    """
    刷新Access Token接口
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        POST /api/auth/refresh/
        
        请求体：
        {
            "refresh": "xxx"
        }
        """
        # 在urls.py中已经使用了rest_framework_simplejwt.views.TokenRefreshView来处理刷新Token的逻辑，因此这里不需要再实现一次。
        return Response(
            {'message': 'Token刷新成功'},
            status=status.HTTP_200_OK,
        )

class UserInfoView(APIView):
    """
    获取用户信息接口
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        GET /api/auth/info/
        
        请求头: Authorization: Bearer <access_token>
        """
        user = request.user
        return Response(
            {
                "user": UserSerializer(user).data
            },
            status=status.HTTP_200_OK,
        )
        
class UserLogoutView(APIView):
    """
    用户登出接口
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        POST /api/auth/logout/
        """
        return Response(
            {'message': '登出成功'},
            status=status.HTTP_200_OK,
        )