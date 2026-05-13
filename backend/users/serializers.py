from rest_framework import serializers
from .models import User
import re


class RegisterSerializer(serializers.Serializer):
    """自定义序列化器，用于注册验证"""
    username = serializers.CharField(required=True, allow_blank=False)
    phone = serializers.CharField(required=True, allow_blank=False)
    password = serializers.CharField(required=True, write_only=True)
    password_confirm = serializers.CharField(required=False, write_only=True, allow_blank=True)
    id = serializers.IntegerField(read_only=True)

    def validate_username(self, value):
        """验证用户名"""
        if not value or not value.strip():
            raise serializers.ValidationError("用户名不能为空")
        if len(value) < 2:
            raise serializers.ValidationError("用户名至少2个字符")
        if len(value) > 150:
            raise serializers.ValidationError("用户名最多150个字符")
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("用户名已被注册")
        return value

    def validate_phone(self, value):
        """验证电话号码"""
        if not value or not value.strip():
            raise serializers.ValidationError("电话号码不能为空")
        # 简单的格式检查：至少5个数字
        if not re.search(r'\d{5,}', value):
            raise serializers.ValidationError("电话号码格式不正确（至少包含5个数字）")
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("电话号码已有账户，请重试")
        return value

    def validate_password(self, value):
        """验证密码"""
        if not value or not value.strip():
            raise serializers.ValidationError("密码不能为空")
        if len(value) < 6:
            raise serializers.ValidationError("密码至少6个字符")
        return value

    def validate(self, data):
        """跨字段验证"""
        # 如果提供了密码确认，检查两个密码是否一致
        if data.get('password_confirm') and data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({"password": "两次输入的密码不一致"})
        return data

    def create(self, validated_data):
        """创建用户"""
        validated_data.pop('password_confirm', None)
        user = User.objects.create_user(
            username=validated_data['username'],


            class UserSerializer(serializers.ModelSerializer):
                class Meta:
                    model = User
                    fields = ('id', 'username', 'phone')
            password=validated_data['password'],
            phone=validated_data['phone']
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'phone')

    def create(self, validated_data):
        """创建用户"""
        validated_data.pop('password_confirm', None)
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            phone=validated_data['phone']
        )
        return user
