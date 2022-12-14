# from rest_framework import serializers
# from account.models import User 

# class UserRegistrationSerializer(serializers.ModelSerializer):
#     # We are writing this bcoz we need confirm password field
#     #  in our Registration Request
#     password2 = serializers.CharField(style={'input_type':'password'},read_only=True)
#     class Meta:
#         model = User 
#         fields = ['email', 'name', 'password', 'password2', 'tc']
#         extra_kwargs={
#             'password':{'write_only':True}
#         }

#         # validating password and confirm password while Registration
#         def validate(self, attrs):
#             password = attrs.get('password')
#             password2 = attrs.get('password2')
#             if password != password2:
#                 raise serializers.ValidationError("Password and Confirm Password does not match")
#             return attrs

#         def create(self, validate_data):
#             return User.objects.create_user(**validate_data)    


# from unittest.util import 

from xml.dom import ValidationErr
from rest_framework import serializers
from account.models import User
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator

from account.utils import Util  
# from formatter import _StylesType

class UserRegistrationSerializer(serializers.ModelSerializer):
    #we are writing this bcoz we need confirm password feild in our Registration Request
    password2 = serializers.CharField(style={'input_type':'password'}
    , write_only=True)
    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'password2', 'tc']
        extra_kwargs={
            'password':{'write_only':True}
        }
    # Validing password and confirm password while registraion 
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password and confirm password does not match")
        return attrs
    def create(self, validate_data):
        return User.objects.create_user(**validate_data)    

class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = User
        fields = ['email', 'password']
        # field = '__all__'
       
class  UserProfileSerializer(serializers.ModelSerializer):
    class  Meta:
        model = User
        fields = ['id', 'email', 'name']       

class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=250, style=
    {'input_type':'password'}, write_only=True)
    password2 = serializers.CharField(max_length=250, style=
    {'input_type':'password'}, write_only=True)
    class Meta:
        fields = ['password', 'password2']
    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')
        if password != password2:
            raise serializers.ValidationError("Password and confirm password does not match")
        user.set_password(password)
        user.save()
        return attrs
 
class SendPasswordResetEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=250)
    class Meta:
        fields = ['email'] 
    def validate(self, attrs):
        email = attrs.get('email')
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            print('Encoded UID', uid)
            token = PasswordResetTokenGenerator().make_token(user)
            print('Password Reset Token', token)
            link = 'http://localhost:3000/api/user/reset/'+ uid + '/' + token
            print('Password reset link', link)
            # send email
            body  = 'Click following link to reset your password' + link
            data = {
                'subject':'Reset your password',
                'body':body,
                'to_email':user.email
            }
            Util.send_email(data)
            return attrs
        else:
            raise ValidationErr('You are not a registered user')
        # return super().validate(attrs)    

class UserPasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField(max_length=250, style=
    {'input_type':'password'}, write_only=True)
    password2 = serializers.CharField(max_length=250, style=
    {'input_type':'password'}, write_only=True)
    class Meta:
        fields = ['password', 'password2']
    def validate(self, attrs):
        try:
            password = attrs.get('password')
            password2 = attrs.get('password2')
            uid = self.context.get('uid')
            token = self.context.get('token')
            if password != password2:
                raise serializers.ValidationError("Password and confirm password does not match")
            id = smart_str(urlsafe_base64_decode(uid)) 
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise ValidationErr('Token is not valid or expired')   
            user.set_password(password)
            user.save()
            return attrs 
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token) 
            raise ValidationErr('Token is not valid or expired')      


