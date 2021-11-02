import json, jwt

from django.test import TestCase, Client, client

from .models import Category, Post
from users.models import User
from my_settings import ALGORITHM, SECRET_KEY

class PostListTest(TestCase):
    def setUp(self):
        User.objects.create(
            id = 1,
            name = "최현수",
            password = "q1w2e3r!",
            email = "chs@naver.com",
            nickname = "hs"
        )
        self.token = jwt.encode({'id' :User.objects.get(id=1).id}, SECRET_KEY, algorithm = ALGORITHM)
        
        User.objects.create(
            id = 2,
            name = "김상만",
            password = "q1w2e3r!",
            email = "sm@naver.com",
            nickname = "sm"
        )
        Category.objects.create(
            id=1,
            name="자유게시판"
        )

        Post.objects.create(
            id=1,
            title = "first",
            body = "wanted",
            user = User.objects.get(id=1),
            category_id = Category.objects.get(id=1).id
        )

        Post.objects.create(
            id=2,
            title = "second",
            body = "wecode",
            user = User.objects.get(id=1),
            category_id = Category.objects.get(id=1).id
        )

        Post.objects.create(
            id=3,
            title = "third",
            body = "love it",
            user = User.objects.get(id=1),
            category_id = Category.objects.get(id=1).id
        ),
        Post.objects.create(
            id=5,
            title = "fivth",
            body = "love",
            user = User.objects.get(id=2),
            category_id = Category.objects.get(id=1).id
        )
        
        
    def tearDown(self):
        Post.objects.all().delete()
        User.objects.all().delete()
        Category.objects.all().delete()

    def test_get_post_list_success(self):
        client = Client()

        response = client.get('/post/list')

        self.assertEqual(response.json(),{
            "Result" : [
            {
                "count": 4,
                "title": "fivth",
                "hit": 0,
                "body": "love",
                "nickname": "sm"
            },
            {
                "count": 3,
                "title": "third",
                "hit": 0,
                "body": "love it",
                "nickname": "hs"
            },
            {
                "count": 2,
                "title": "second",
                "hit": 0,
                "body": "wecode",
                "nickname": "hs"
            },
            {
                "count": 1,
                "title": "first",
                "hit": 0,
                "body": "wanted",
                "nickname": "hs"
            }]
        })
        self.assertEqual(response.status_code, 200)
    
    def test_get_post_list_page_not_found(self):
        client = Client()

        response = client.get('/post/list?page=10')
        
        self.assertEqual(response.json(),{
            "message" : "PAGE_NOT_FOUND"
        })
        self.assertEqual(response.status_code, 404)
    
    def test_get_post_list_category_not_found(self):
        client = Client()

        response = client.get('/post/list?category=대한민국')
        
        self.assertEqual(response.json(),{
            "message" : "CATEGORY_NOT_FOUND"
        })
        self.assertEqual(response.status_code, 404)

    def test_get_post_success(self):
        client = Client()
        
        header       = {"HTTP_Authorization" : self.token}
        token        = header['HTTP_Authorization']
        
        created_at = Post.objects.get(id=3).created_at
        updated_at = Post.objects.get(id=3).updated_at

        response = client.get('/post/detail/3', **header, content_type='application/json')

        self.assertEqual(response.json(),{
            "Result" : {
                "body": "love it",
                "create_at" : created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "hit": 1,
                "category": "자유게시판",
                "nickname": "hs",
                "title": "third",
                "update_at" : updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            })
        self.assertEqual(response.status_code, 200)

    def test_get_post_posts_not_found(self):
        client = Client()
        
        header       = {"HTTP_Authorization" : self.token}
        token        = header['HTTP_Authorization']
        
        response = client.get('/post/detail/50', **header, content_type='application/json')

        self.assertEqual(response.json(),{
            "message" : "POSTS_NOT_FOUND"
            })
        self.assertEqual(response.status_code, 404)

    def test_post_post_success(self):
        client = Client()
        
        header       = {"HTTP_Authorization" : self.token}
        token        = header['HTTP_Authorization']
        
        payload      = jwt.decode(token, SECRET_KEY, algorithms = ALGORITHM)
        user         = User.objects.get(id = payload['id'])
        
        post = {
            "id" : 4,
            'user' : user.id,
            'category' : '자유게시판',
            'title' : 'fourth',
            'body' : 'love too'
        }
    
        response = client.post("/post/list", json.dumps(post), **header, content_type='application/json')
       
        self.assertEqual(response.json(),{
            "message" : "SUCCESS"
        })
        self.assertEqual(response.status_code, 201)

    def test_post_post_key_error(self):
        client = Client()
        
        header       = {"HTTP_Authorization" : self.token}
        token        = header['HTTP_Authorization']
        
        payload      = jwt.decode(token, SECRET_KEY, algorithms = ALGORITHM)
        user         = User.objects.get(id = payload['id'])
        
        post = {
            "id" : 4,
            'user' : user.id,
            'title' : 'fourth',
        }
    
        response = client.post("/post/list", json.dumps(post), **header, content_type='application/json')
       
        self.assertEqual(response.json(),{
            "message" : "KEY_ERROR"
        })
        self.assertEqual(response.status_code, 400)

    def test_post_post_category_not_found(self):
        client = Client()
        
        header       = {"HTTP_Authorization" : self.token}
        token        = header['HTTP_Authorization']
        
        payload      = jwt.decode(token, SECRET_KEY, algorithms = ALGORITHM)
        user         = User.objects.get(id = payload['id'])
        
        post = {
            "id" : 4,
            'user' : user.id,
            'category' : 1,
            'title' : 'fourth',
        }
    
        response = client.post("/post/list", json.dumps(post), **header, content_type='application/json')
       
        self.assertEqual(response.json(),{
            "message" : "CATEGORY_NOT_FOUND"
        })
        self.assertEqual(response.status_code, 404)

    def test_put_post_update_success(self):
        client = Client()
        
        header       = {"HTTP_Authorization" : self.token}
        token        = header['HTTP_Authorization']
        
        payload      = jwt.decode(token, SECRET_KEY, algorithms = ALGORITHM)
        user         = User.objects.get(id = payload['id'])
        
        post = {
            "id" : 4,
            'user' : user.id,
            'category' : "자유게시판",
            'title' : 'fourth',
            'body' : 'love too'
        }
    
        response = client.put("/post/detail/1", json.dumps(post), **header, content_type='application/json')
       
        self.assertEqual(response.json(),{
            "message" : "SUCCESS"
        })
        self.assertEqual(response.status_code, 201)
    
    def test_put_post_key_error(self):
        client = Client()
        
        header       = {"HTTP_Authorization" : self.token}
        token        = header['HTTP_Authorization']
        
        payload      = jwt.decode(token, SECRET_KEY, algorithms = ALGORITHM)
        user         = User.objects.get(id = payload['id'])
        
        post = {
            "id" : 4,
            'user' : user.id,
            'body' : 'love too'
        }
    
        response = client.put("/post/detail/1", json.dumps(post), **header, content_type='application/json')
       
        self.assertEqual(response.json(),{
            "message" : "KEY_ERROR"
        })
        self.assertEqual(response.status_code, 400)

    def test_put_post_not_exists(self):
        client = Client()
        
        header       = {"HTTP_Authorization" : self.token}
        token        = header['HTTP_Authorization']
        
        payload      = jwt.decode(token, SECRET_KEY, algorithms = ALGORITHM)
        user         = User.objects.get(id = payload['id'])
        
        post = {
            "id" : 4,
            'user' : user.id,
            'body' : 'love too'
        }
    
        response = client.put("/post/detail/100", json.dumps(post), **header, content_type='application/json')
       
        self.assertEqual(response.json(),{
            "message" : "POST_NOT_FOUND"
        })
        self.assertEqual(response.status_code, 404)
    
    def test_put_category_not_exists(self):
        client = Client()
        
        header       = {"HTTP_Authorization" : self.token}
        token        = header['HTTP_Authorization']
        
        payload      = jwt.decode(token, SECRET_KEY, algorithms = ALGORITHM)
        user         = User.objects.get(id = payload['id'])
        
        post = {
            "id" : 4,
            'category' : "대한민국",
            'user' : user.id,
            'body' : 'love too'
        }
    
        response = client.put("/post/detail/1", json.dumps(post), **header, content_type='application/json')
       
        self.assertEqual(response.json(),{
            "message" : "CATEGORY_NOT_FOUND"
        })
        self.assertEqual(response.status_code, 404)

    def test_put_post_permission_deny(self):
        client = Client()
        
        header       = {"HTTP_Authorization" : self.token}
        token        = header['HTTP_Authorization']
        
        payload      = jwt.decode(token, SECRET_KEY, algorithms = ALGORITHM)
        user         = User.objects.get(id = payload['id'])
        
        post = {
            "id" : 5,
            'user' : user.id,
            'title' : 'hello',
            'body' : 'love too'
        }
    
        response = client.put("/post/detail/5", json.dumps(post), **header, content_type='application/json')
       
        self.assertEqual(response.json(),{
            "message" : "NO_PERMISSION"
        })
        self.assertEqual(response.status_code, 401)

    def test_delete_post_success(self):
        client = Client()

        header       = {"HTTP_Authorization" : self.token}

        response = client.delete("/post/detail/1", **header)
        
        self.assertEqual(response.json(),{
            "message" : "POST_DELETED"
        })
        self.assertEqual(response.status_code, 200)

    def test_delete_post_not_exists(self):
        client = Client()

        header       = {"HTTP_Authorization" : self.token}

        response = client.delete("/post/detail/100", **header)
        
        self.assertEqual(response.json(),{
            "message" : 'POST_DOES_NOT_EXIST'
        })
        self.assertEqual(response.status_code, 404)
    
    def test_delete_post_permission_deny(self):
        client = Client()

        header       = {"HTTP_Authorization" : self.token}
        token        = header['HTTP_Authorization']

        response = client.delete("/post/detail/5", **header)
        
        self.assertEqual(response.json(),{
            "message" : "NO_PERMISSION"
        })
        self.assertEqual(response.status_code, 401)
        
