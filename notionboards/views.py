import json
from unittest import result
from django.core.exceptions import ObjectDoesNotExist

from django.http import JsonResponse
from django.db import transaction

from users.decorator import login_decorator
from .models import Category, Post
from django.views import View

class ListView(View):
    def get(self, request):
        try:
            category   = request.GET.get("category")
            page       = request.GET.get("page")
            page       = int(page or 1)
            page_size  = 10
            limit      = page_size * page 
            offset     = limit - page_size
            
            if category:
                category_id = Category.objects.get(name=category).id
                posts = Post.objects.filter(category_id=category_id).order_by('-id')
            else:
                posts = Post.objects.all().order_by('-id')
            
            if not posts [offset:limit]:
                return JsonResponse({"message" : "PAGE_NOT_FOUND"}, status=404)
            
            result = [{
                "count" : len(posts)-(offset+i),
                "title" : post.title,
                "hit" : post.hit,
                "body" : post.body,
                "nickname" : post.user.nickname
            } for i,post in enumerate(posts [offset:limit])]
            
            return JsonResponse({"Result" : result}, status=200)
        except Category.DoesNotExist:
            return JsonResponse({"message" : "CATEGORY_NOT_FOUND"}, status=404)

    @transaction.atomic
    @login_decorator
    def post(self, request):
        data = json.loads(request.body)
        user = request.user

        try:
            category = Category.objects.get(name=data['category'])
            Post.objects.create(
                title = data['title'],
                body = data['body'],
                user_id = user.id,
                category_id = category.id
            )
            return JsonResponse({"message" : "SUCCESS"}, status=201)
        except KeyError:
            return JsonResponse({"message" : "KEY_ERROR"}, status=400)
        except Category.DoesNotExist:
            return JsonResponse({"message" : "CATEGORY_NOT_FOUND"}, status=404)

class PostView(View):
    @transaction.atomic
    @login_decorator
    def get(self, request,post_id):
        try:
            post = Post.objects.get(id=post_id)
            
            result = {
                "title" : post.title,
                "body" : post.body,
                "hit" : post.hit,
                "category" : Category.objects.get(id=post.category.id).name,
                "create_at" : post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "update_at" : post.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                "nickname" : post.user.nickname
            }
            
            response = JsonResponse({"Result" : result}, status=200)
            
            if request.COOKIES.get('hit'):
                cookies = request.COOKIES.get('hit')
                cookies_list = cookies.split('|')
                if str(post.id) not in cookies_list:
                    
                    post.hit += 1
                    post.save()

                    result["hit"] = post.hit
                    response = JsonResponse({"Result" : result}, status=200)
                    
                    response.set_cookie('hit', cookies+f'|{post.id}', expires=None)
            else:
                post.hit += 1
                post.save()
  
                result["hit"] = post.hit
                response = JsonResponse({"Result" : result}, status=200)
            
                response.set_cookie('hit', post.id, expires=None)
            return response
        except Post.DoesNotExist:
            return JsonResponse({"message" : "POSTS_NOT_FOUND"}, status=404)

    @transaction.atomic
    @login_decorator
    def put(self, request, post_id):
        data = json.loads(request.body)
        user = request.user
        try:
            post = Post.objects.get(id=post_id)
            
            if not (post.user_id == user.id):
                return JsonResponse({"message" : "NO_PERMISSION"}, status=401)
            
            category = Category.objects.get(name=data["category"])
            
            post.category_id = category.id
            post.title = data["title"]
            post.body = data["body"]
            post.save()

            return JsonResponse({"message" : "SUCCESS"}, status=201)
        except KeyError:
            return JsonResponse({"message" : "KEY_ERROR"}, status=400)
        except Post.DoesNotExist:
            return JsonResponse({"message" : "POST_NOT_FOUND"}, status=404)
        except Category.DoesNotExist:
            return JsonResponse({"message" : "CATEGORY_NOT_FOUND"}, status=404)
            
    
    @login_decorator
    def delete(self, request, post_id):
        user = request.user

        try:
            post = Post.objects.get(id=post_id)
            
            if post.user_id != user.id:
                return JsonResponse({"message" : "NO_PERMISSION"}, status=401)
            
            post.delete()
            
            return JsonResponse({'message': 'POST_DELETED'}, status=200)
        
        except ObjectDoesNotExist:
            return JsonResponse({'message': 'POST_DOES_NOT_EXIST'}, status=404)