from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class UserRegisterSerializer(serializers.ModelSerializer):
    """
    用户注册序列化器
    """
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        help_text="密码至少8位,且包含字母和数字",
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        help_text="确认密码",
    )
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'password2')
        extra_kwargs = {
            'username': {
                'required': True,
                'help_text': '用户名不能为空'
            },
            'email': {
                'required': True,
                'help_text': '邮箱不能为空'
            },
        }
    
    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {"password": "两次输入的密码不匹配"}
            )
        return data

    def validate_username(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("用户名至少3个字符")
        elif len(value) > 30:
            raise serializers.ValidationError("用户名不能超过30个字符")
        else:
            for i in value:
                if not (i.isalnum() or i == '_' or '\u4e00' <= i <= '\u9fff'):
                    raise serializers.ValidationError("用户名只能包含中文字符、字母、数字和下划线")
        return value
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("该邮箱已被注册")
        return value

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user

class UserLoginSerializer(serializers.Serializer):
    """
    用户登录序列化器
    """
    email = serializers.CharField(required=True, help_text="邮箱")
    password = serializers.CharField(required=True, write_only=True, help_text="密码")
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        user = User.objects.filter(email=email).first()
        if user is None:
            raise serializers.ValidationError("邮箱不正确")
        
        if not user.check_password(password):
            raise serializers.ValidationError("密码不正确")
        
        data['user'] = user
        return data
    
class UserSerializer(serializers.ModelSerializer):
    """
    用户信息序列化器
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        read_only_fields = ('id',)
        
        