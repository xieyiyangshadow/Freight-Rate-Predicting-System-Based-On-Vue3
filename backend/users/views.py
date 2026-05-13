from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate, login
from .serializers import RegisterSerializer, UserSerializer
from .models import User

class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # 自动登录（session）
            authenticated_user = authenticate(username=user.username, password=request.data['password'])
            if authenticated_user:
                login(request, authenticated_user)
                user = authenticated_user
            return Response(UserSerializer(user).data)
        
        # 构建友好的错误提示
        errors = serializer.errors
        error_messages = []
        
        for field, messages in errors.items():
            if isinstance(messages, list) and len(messages) > 0:
                # 取第一条错误信息
                error_messages.append(str(messages[0]))
            elif isinstance(messages, list):
                error_messages.append(f"{field}：格式不正确")
            else:
                error_messages.append(str(messages))
        
        # 如果有多条错误，合并显示
        detail = " | ".join(error_messages) if error_messages else "注册信息不完整或格式不正确"
        
        return Response({'detail': detail}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    def post(self, request):
        phone = request.data.get('phone')
        password = request.data.get('password')
        
        if not phone or not phone.strip():
            return Response({'detail': '请输入电话号码'}, status=status.HTTP_400_BAD_REQUEST)
        if not password:
            return Response({'detail': '请输入密码'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response({'detail': '电话号码不存在，请检查或先注册'}, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=user.username, password=password)
        if user:
            login(request, user)
            return Response(UserSerializer(user).data)
        
        return Response({'detail': '密码错误'}, status=status.HTTP_400_BAD_REQUEST)
