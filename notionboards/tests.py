import json, jwt

from django.test import TestCase, Client, client

from .models import Notion
from users.models import User
from my_settings import ALGORITHM, SECRET_KEY

class NotionListTest(TestCase):
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
        Notion.objects.create(
            id=1,
            title = "first",
            body = "wanted",
            user = User.objects.get(id=1),
        )

        Notion.objects.create(
            id=2,
            title = "second",
            body = "wecode",
            user = User.objects.get(id=1),
        )

        Notion.objects.create(
            id=3,
            title = "third",
            body = "love it",
            user = User.objects.get(id=1),
        ),
        Notion.objects.create(
            id=5,
            title = "fivth",
            body = "love",
            user = User.objects.get(id=2),
        )
        
        
        
    def tearDown(self):
        Notion.objects.all().delete()
        User.objects.all().delete()
    
    def test_get_notion_list_success(self):
        client = Client()

        response = client.get('/notion/list')

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
            }],
            "page" : 1
        })
        self.assertEqual(response.status_code, 200)
    
    def test_get_notion_list_page_not_found(self):
        client = Client()

        response = client.get('/notion/list?page=10')
        
        self.assertEqual(response.json(),{
            "message" : "PAGE_NOT_FOUND"
        })
        self.assertEqual(response.status_code, 404)

    def test_get_notion_success(self):
        client = Client()
        
        created_at = Notion.objects.get(id=3).created_at
        updated_at = Notion.objects.get(id=3).updated_at

        response = client.get('/notion/detail?id=3')

        self.assertEqual(response.json(),{
            "Result" : {
                "body": "love it",
                "create_at" : created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "hit": 1,
                "nickname": "hs",
                "title": "third",
                "update_at" : updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            })
        self.assertEqual(response.status_code, 200)

    def test_get_notion_notions_not_found(self):
        client = Client()
    
        response = client.get('/notion/detail?id=50')

        self.assertEqual(response.json(),{
            "message" : "NOTIONS_NOT_FOUND"
            })
        self.assertEqual(response.status_code, 404)

    def test_post_notion_success(self):
        client = Client()
        
        header       = {"HTTP_Authorization" : self.token}
        token        = header['HTTP_Authorization']
        
        payload      = jwt.decode(token, SECRET_KEY, algorithms = ALGORITHM)
        user         = User.objects.get(id = payload['id'])
        
        notion = {
            "id" : 4,
            'user' : user.id,
            'title' : 'fourth',
            'body' : 'love too'
        }
    
        response = client.post("/notion/list", json.dumps(notion), **header, content_type='application/json')
       
        self.assertEqual(response.json(),{
            "message" : "SUCCESS"
        })
        self.assertEqual(response.status_code, 201)

    def test_post_notion_key_error(self):
        client = Client()
        
        header       = {"HTTP_Authorization" : self.token}
        token        = header['HTTP_Authorization']
        
        payload      = jwt.decode(token, SECRET_KEY, algorithms = ALGORITHM)
        user         = User.objects.get(id = payload['id'])
        
        notion = {
            "id" : 4,
            'user' : user.id,
            'title' : 'fourth',
        }
    
        response = client.post("/notion/list", json.dumps(notion), **header, content_type='application/json')
       
        self.assertEqual(response.json(),{
            "message" : "KEY_ERROR"
        })
        self.assertEqual(response.status_code, 400)

    def test_put_notion_update_success(self):
        client = Client()
        
        header       = {"HTTP_Authorization" : self.token}
        token        = header['HTTP_Authorization']
        
        payload      = jwt.decode(token, SECRET_KEY, algorithms = ALGORITHM)
        user         = User.objects.get(id = payload['id'])
        
        notion = {
            "id" : 4,
            'user' : user.id,
            'title' : 'fourth',
            'body' : 'love too'
        }
    
        response = client.put("/notion/detail?id=1", json.dumps(notion), **header, content_type='application/json')
       
        self.assertEqual(response.json(),{
            "message" : "SUCCESS"
        })
        self.assertEqual(response.status_code, 201)
    
    def test_put_notion_key_error(self):
        client = Client()
        
        header       = {"HTTP_Authorization" : self.token}
        token        = header['HTTP_Authorization']
        
        payload      = jwt.decode(token, SECRET_KEY, algorithms = ALGORITHM)
        user         = User.objects.get(id = payload['id'])
        
        notion = {
            "id" : 4,
            'user' : user.id,
            'body' : 'love too'
        }
    
        response = client.put("/notion/detail?id=1", json.dumps(notion), **header, content_type='application/json')
       
        self.assertEqual(response.json(),{
            "message" : "KEY_ERROR"
        })
        self.assertEqual(response.status_code, 400)

    def test_put_notion_not_exists(self):
        client = Client()
        
        header       = {"HTTP_Authorization" : self.token}
        token        = header['HTTP_Authorization']
        
        payload      = jwt.decode(token, SECRET_KEY, algorithms = ALGORITHM)
        user         = User.objects.get(id = payload['id'])
        
        notion = {
            "id" : 4,
            'user' : user.id,
            'body' : 'love too'
        }
    
        response = client.put("/notion/detail?id=100", json.dumps(notion), **header, content_type='application/json')
       
        self.assertEqual(response.json(),{
            "message" : "NOTION_NOT_FOUND"
        })
        self.assertEqual(response.status_code, 404)

    def test_put_notion_permission_deny(self):
        client = Client()
        
        header       = {"HTTP_Authorization" : self.token}
        token        = header['HTTP_Authorization']
        
        payload      = jwt.decode(token, SECRET_KEY, algorithms = ALGORITHM)
        user         = User.objects.get(id = payload['id'])
        
        notion = {
            "id" : 5,
            'user' : user.id,
            'title' : 'hello',
            'body' : 'love too'
        }
    
        response = client.put("/notion/detail?id=5", json.dumps(notion), **header, content_type='application/json')
       
        self.assertEqual(response.json(),{
            "message" : "NO_PERMISSION"
        })
        self.assertEqual(response.status_code, 401)

    def test_delete_notion_success(self):
        client = Client()

        header       = {"HTTP_Authorization" : self.token}

        response = client.delete("/notion/detail?id=1", **header)
        
        self.assertEqual(response.json(),{
            "message" : "NOTION_DELETED"
        })
        self.assertEqual(response.status_code, 200)

    def test_delete_notion_not_exists(self):
        client = Client()

        header       = {"HTTP_Authorization" : self.token}

        response = client.delete("/notion/detail?id=100", **header)
        
        self.assertEqual(response.json(),{
            "message" : 'NOTION_DOES_NOT_EXIST'
        })
        self.assertEqual(response.status_code, 404)
    
    def test_delete_notion_permission_deny(self):
        client = Client()

        header       = {"HTTP_Authorization" : self.token}
        token        = header['HTTP_Authorization']

        response = client.delete("/notion/detail?id=5", **header)
        
        self.assertEqual(response.json(),{
            "message" : "NO_PERMISSION"
        })
        self.assertEqual(response.status_code, 401)
        
class ListSearchTest(TestCase):
    def setUp(self):
        User.objects.create(
            id = 1,
            name = "최현수",
            password = "q1w2e3r!",
            email = "chs@naver.com",
            nickname = "hs"
        )
        self.token = jwt.encode({'id' :User.objects.get(id=1).id}, SECRET_KEY, algorithm = ALGORITHM)

        Post.objects.create(
            id=1,
            title = "first",
            body = "wanted",
            user = User.objects.get(id=1),
        )

        Post.objects.create(
            id=2,
            title = "second",
            body = "wecode",
            user = User.objects.get(id=1),
        )
    
    def tearDwon(self):
        Post.objects.all().delete()

    def test_search_post_success(self):
        client = Client()

        search_word = {
            "search_word" : "wecode"
        }

        response = client.post("/post/search", json.dumps(search_word), content_type="apllication/json")

        self.assertEqual(response.json(), {
            "Result": [
                {
                    "title": "second",
                    "user": "최현수",
                    "body": "wecode"
                    }]
                }
            )
        self.assertEqual(response.status_code, 200)

    def test_search_post_wrong_request_empty(self):
        client = Client()

        search_word = {
            "search_word" : ""
        }

        response = client.post("/post/search", json.dumps(search_word), content_type="apllication/json")

        self.assertEqual(response.json(), {"message" : "WRONG_REQUEST"})
        self.assertEqual(response.status_code, 401)

    def test_search_post_wrong_request_space(self):
        client = Client()

        search_word = {
            "search_word" : " "
        }

        response = client.post("/post/search", json.dumps(search_word), content_type="apllication/json")

        self.assertEqual(response.json(), {"message" : "WRONG_REQUEST"})
        self.assertEqual(response.status_code, 401)

    def test_search_post_wrong_request_too_long(self):
        client = Client()

        search_word = {
            "search_word" : "abcdefghijklmnopqrstuvwxyzabcdefg"
        }

        response = client.post("/post/search", json.dumps(search_word), content_type="apllication/json")

        self.assertEqual(response.json(), {"message" : "WRONG_REQUEST"})
        self.assertEqual(response.status_code, 401)
        
    def test_search_post_key_error(self):
        client = Client()

        search_word = {
            "search_words" : "wecode"
        }

        response = client.post("/post/search", json.dumps(search_word), content_type="apllication/json")

        self.assertEqual(response.json(), {"message" : "KEY_ERROR"})
        self.assertEqual(response.status_code, 400)