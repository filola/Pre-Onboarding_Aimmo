import json, bcrypt, jwt

from django.test import TestCase, Client

from .models import User
from my_settings import SECRET_KEY, ALGORITHM

class SignUpTest(TestCase):
    def setUp(self):
        User.objects.create(
            name = "최현수",
            password = "q1w2e3r!",
            email = "chs@naver.com",
            nickname = "hs"
        )

    def tearDown(self):
        User.objects.all().delete()

    def test_signup_view_create_user_success(self):
        client = Client()

        user = {
            'name' : '최현수',
            'email' : 'chs00@naver.com',
            'password' : 'q1w2e3r!',
            'nickname' : 'hs'
        }
        
        response = client.post('/user/signup', json.dumps(user), content_type='application/json')

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(),{
                            "Message" : "SUCCESS"
                        }
                    )

    def test_signup_view_invalid_email(self):
        client = Client()
        
        user = {
            'name' : '최현수',
            'email' : 'chsnaver.com',
            'password' : 'q1w2e3r!',
            'nickname' : 'hs'
            }
        
        response = client.post('/user/signup', json.dumps(user), content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
                        {
                            "message" : "INVALID_EMAIL_FORMAT"
                        }
                    )
    
    def test_signup_view_invalid_password(self):
        client = Client()
        
        user = {
            'name' : '최현수',
            'email' : 'chs@naver.com',
            'password' : 'q1w',
            'nickname' : 'hs'
            }
        
        response = client.post('/user/signup', json.dumps(user), content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
                        {
                            "message" : "INVALID_PASSWORD_FORMAT"
                        }
                    )

    def test_signup_view_same_email_exists(self):
        client = Client()

        user = {
            'name' : '최현수',
            'email' : 'chs@naver.com',
            'password' : 'q1w2e3r!',
            'nickname' : 'hs'
        }
        
        response = client.post('/user/signup', json.dumps(user), content_type='application/json')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
                            "message" : "SAME_EMAIL_EXISTS"
                        }
                    )
    
    def test_signup_view_key_error(self):
        client = Client()
        
        user = {
            'name' : '최현수',
            'email' : 'chs12@naver.com',
            'password' : 'q1w2e3r!',
            'nicknames' : 'hs'
        }
        response = client.post('/user/signup', json.dumps(user), content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
                        {
                            "Message" : "KEY_ERROR"
                        }
                    )
    
    def test_signup_view_data_error(self):
        client = Client()
        
        user = {
            'name' : '최현수',
            'email' : 'chs12@naver.com',
            'password' : 'q1w2e3r!',
            'nicknames' : 'hs'
        }
        response = client.post('/user/signup', json.dumps(user), content_type='application/json')
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),
                        {
                            "Message" : "KEY_ERROR"
                        }
                    )

class LoginTest(TestCase):
    def setUp(self):
        User.objects.create(
            name = "최현수",
            password = "$2b$12$3HxA/retVhtxFXyYZ.vGSOGV4.LDVZkWUIcCIvv2bBN0RqlhLiVFC",
            email = "chs@naver.com",
            nickname = "hs"
        )

    def tearDown(self):
        User.objects.all().delete()

    def test_login_view_user_success(self):
        client = Client()

        login_user = {
            'email' : 'chs@naver.com',
            'password' : 'q1w2e3r!',
        }
        user = User.objects.get(email = login_user['email'])
        
        access_token = jwt.encode({'id' : user.id}, SECRET_KEY, algorithm = ALGORITHM)
        response     = client.post('/user/login', json.dumps(login_user), content_type = 'application/json')
            
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(),{
                            "Message" : "SUCCESS",
                            "token" : access_token
                        }
                    )

    def test_login_view_invalid_user(self):
        client = Client()

        login_user = {
            'email' : 'chs11@naver.com',
            'password' : 'q1w2e3r!',
        }
        response     = client.post('/user/login', json.dumps(login_user), content_type = 'application/json')
            
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(),{
                            "Message" : "INVALID_USER",
                        }
                    )

    def test_login_view_password_error(self):
        client = Client()

        login_user = {
            'email' : 'chs@naver.com',
            'password' : 'q1w2e3r!aa',
        }
        response     = client.post('/user/login', json.dumps(login_user), content_type = 'application/json')
            
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(),{
                            "Message" : "PASSWORD_ERROR",
                        }
                    )
    
    def test_login_view_key_error(self):
        client = Client()

        login_user = {
            'password' : 'q1w2e3r!aa',
        }
        response     = client.post('/user/login', json.dumps(login_user), content_type = 'application/json')
            
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(),{
                            "Message" : "KEY_ERROR",
                        }
                    )