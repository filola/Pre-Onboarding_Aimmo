import json
from unittest import result
from django.core.exceptions import ObjectDoesNotExist

from django.http import JsonResponse

from users.decorator import login_decorator
from .models import Post
from django.views import View

class ListView(View):
    def get(self, request):
        page       = request.GET.get("page", 1)
        page       = int(page or 1)
        page_size  = 10
        limit      = page_size * page 
        offset     = limit - page_size
        
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
        
        return JsonResponse({"Result" : result, "page" : page}, status=200)

    @login_decorator
    def post(self, request):
        data = json.loads(request.body)
        user = request.user

        try:
            result=Post.objects.create(
                title = data['title'],
                body = data['body'],
                user_id = user.id
            )
            return JsonResponse({"message" : "SUCCESS"}, status=201)
        except KeyError:
            return JsonResponse({"message" : "KEY_ERROR"}, status=400)

@login_decorator
class PostView(View):
    def get(self, request):
        post_id = request.GET.get("id")

        try:
            post = Post.objects.get(id=post_id)
            
            post.hit += 1
            post.save()
            
            result = {
                "title" : post.title,
                "body" : post.body,
                "hit" : post.hit,
                "create_at" : post.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "update_at" : post.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                "nickname" : post.user.nickname
            }
            return JsonResponse({"Result" : result}, status=200)
        except Post.DoesNotExist:
            return JsonResponse({"message" : "POSTS_NOT_FOUND"}, status=404)

    @login_decorator
    def put(self, request):
        data = json.loads(request.body)
        post_id = request.GET.get("id")
        user = request.user
        try:
            post = Post.objects.get(id=post_id)
            
            if not (post.user_id == user.id):
                return JsonResponse({"message" : "NO_PERMISSION"}, status=401)
            
            post.title = data["title"]
            post.body = data["body"]
            post.save()

            return JsonResponse({"message" : "SUCCESS"}, status=201)
        except KeyError:
            return JsonResponse({"message" : "KEY_ERROR"}, status=400)
        except Post.DoesNotExist:
            return JsonResponse({"message" : "POST_NOT_FOUND"}, status=404)
    
    @login_decorator
    def delete(self, request):
        post_id = request.GET.get('id')
        user = request.user

        try:
            post = Post.objects.get(id=post_id)
            
            if post.user_id != user.id:
                return JsonResponse({"message" : "NO_PERMISSION"}, status=401)
            
            post.delete()
            
            return JsonResponse({'message': 'POST_DELETED'}, status=200)
        
        except ObjectDoesNotExist:
            return JsonResponse({'message': 'POST_DOES_NOT_EXIST'}, status=404)