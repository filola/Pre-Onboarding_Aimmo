import json, re, jwt, bcrypt

from django.views import View
from django.http import JsonResponse
from .models import User
from django.db.utils import DataError

from my_settings import SECRET_KEY, ALGORITHM

class SignUpView(View):
    def post(self, request):
        data = json.loads(request.body)

        email_format = re.compile("\w+[@]\w+[.]\w+")
        password_format = re.compile("^(?=.*[a-zA-Z])(?=.*[0-9])(?=.*[!@#$%^&*])[a-zA-Z0-9!@#$%^&*]{8,20}$")

        try:
            if not email_format.search(data["email"]):
                return JsonResponse({"message" : "INVALID_EMAIL_FORMAT"}, status=400)

            if not password_format.match(data["password"]):
                return JsonResponse({"message" : "INVALID_PASSWORD_FORMAT"}, status=400)
            
            if User.objects.filter(email=data["email"]).exists():
                return JsonResponse({"message" : "SAME_EMAIL_EXISTS"}, status=400)

            salt = bcrypt.gensalt()
            encode_password = data["password"].encode("utf-8")
            hash_password = bcrypt.hashpw(encode_password, salt)
            decode_password = hash_password.decode("utf-8")

            User.objects.create(
                name=data["name"],
                nickname=data["nickname"],
                email=data["email"],
                password=decode_password
            )
            return JsonResponse({"Message" : "SUCCESS"}, status=201)
        except KeyError:
            return JsonResponse({"Message" : "KEY_ERROR"}, status=400)
        except DataError:
            return JsonResponse({"Message" : "DATA_TOO_LONG"}, statsu=400)

class LoginView(View):
    def post(self, request):
        data = json.loads(request.body)

        try:
            if not User.objects.filter(email=data["email"]).exists():
                return JsonResponse({"Message": "INVALID_USER"}, status=401)

            user = User.objects.get(email=data["email"])

            if not bcrypt.checkpw(
                data["password"].encode("utf-8"), user.password.encode("utf-8")
            ):
                return JsonResponse({"Message": "PASSWORD_ERROR"}, status=401)

            access_token = jwt.encode({"id": user.id}, SECRET_KEY, algorithm=ALGORITHM)
            return JsonResponse({"Message": "SUCCESS", "token": access_token}, status=200)
        
        except KeyError:
            return JsonResponse({"Message" : "KEY_ERROR"}, status=400)