import json
from unittest import result
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from django.http import JsonResponse
from django.db import transaction

from users.decorator import login_decorator
from .models import Category, Post, Comment
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

            limit = int(request.GET.get("limit",3))
            offset = int(request.GET.get("offset",0))

            comments = Comment.objects.filter(posting_id=post_id, parent_comment=None)

            Result_comment = [{
            "comment_id": comment.id,
            "content" : comment.content,
            "parent_comment" : comment.parent_comment_id
            } for comment in comments]

            Result_comment = Result_comment[offset:offset+limit]
            
            response = JsonResponse({"Result" : result, "Comment" : Result_comment}, status=200)
            
            if request.COOKIES.get('hit'):
                cookies = request.COOKIES.get('hit')
                cookies_list = cookies.split('|')
                if str(post.id) not in cookies_list:
                    
                    post.hit += 1
                    post.save()

                    result["hit"] = post.hit
                    response = JsonResponse({"Result" : result, "Comment" : Result_comment}, status=200)
                    
                    response.set_cookie('hit', cookies+f'|{post.id}', expires=None)
            else:
                post.hit += 1
                post.save()
  
                result["hit"] = post.hit
                response = JsonResponse({"Result" : result, "Comment" : Result_comment}, status=200)
            
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
    
class CommentView(View):
    @login_decorator
    def post(self, request, post_id):
        try:
            data = json.loads(request.body)
            user = request.user
            content = data.get("content")
            parent_comment_id = data.get("parent_comment_id")
            posting = Post.objects.get(id=post_id)

            if not Post.objects.filter(id=post_id).exists():
                return JsonResponse({"MESSAGE": "POSTING_DOES_NOT_EXIST"}, status=404)
            
            if content == None:
                return JsonResponse({"MESSAGE": "EMPTY_CONTENT"})

            comment = Comment.objects.create(
                user    = user,
                posting = posting,
                content = content,
                parent_comment_id = parent_comment_id
            )

            if not Comment.objects.get(id=comment.parent_comment_id).parent_comment_id == None:
                return JsonResponse({"MESSAGE": "NO_MORE_COMMENT"})
            
            return JsonResponse({"MESSAGE": "CREATE"}, status=201)
        except KeyError:
            return JsonResponse({"MESSAGE": "KEY_ERROR"}, status=400)


    def get(self, request, post_id):
        
        limit = int(request.GET.get("limit",3))
        offset = int(request.GET.get("offset",0))
        comment_id = request.GET.get("comment_id")
        comments = Comment.objects.filter(parent_comment=comment_id)

        if not Post.objects.filter(id=post_id).exists():
            return JsonResponse({"MESSAGE":"POST_DOES_NOT_EXIST"}, status=404)

        if not Comment.objects.filter(posting=post_id).exists():
            return JsonResponse({"MESSAGE":"COMMENT_DOES_NOT_EXIST"}, status=404)
            
        if not Comment.objects.filter(id=comment_id).exists():
            return JsonResponse({"MESSAGE":"COMMENT_DOES_NOT_EXIST"}, status=404)

        Result = [{
        "comment_id": comment.id,
        "content" : comment.content,
        "parent_comment" : comment.parent_comment_id
        } for comment in comments]

        Result = Result[offset:offset+limit]

        return JsonResponse({"Result":Result}, status=200)
    
    @login_decorator
    def patch(self, request, post_id):
        try:
            if not Post.objects.filter(id=post_id).exists():
                return JsonResponse({"MESSAGE":"DOES_NOT_EXIST"}, status=404)

            data = json.loads(request.body)
            content = data['content']
            comment_id = data['comment_id']

            if not request.user.id == Comment.objects.get(posting=post_id, id=comment_id).user_id:
                return JsonResponse({"MESSAGE":"NOT_MATCHED_USER"}, status=400)

            comment = Comment.objects.filter(posting_id=post_id, user=request.user.id, id=comment_id)
            comment.update(content=content)
            
            return JsonResponse({"MESSAGE":"SUCCESS"}, status=201)

        except KeyError:
            return JsonResponse({"MESSAGE":"KEY_ERROR"}, status=400)

    @login_decorator
    def delete(self, request, post_id):
        comment_id = request.GET.get("comment_id")

        if not Post.objects.filter(id=post_id).exists():
            return JsonResponse({"MESSAGE":"POST_DOES_NOT_EXIST"}, status=404)
        if not Comment.objects.filter(id=comment_id, posting_id=post_id).exists():
            return JsonResponse({"MASSAGE": "COMMENT_DOES_NOT_EXIST"}, status=404)
        if not request.user.id == Comment.objects.get(posting=post_id, id=comment_id).user_id:
                return JsonResponse({"MESSAGE":"NOT_MATCHED_USER"}, status=403)

        comment = Comment.objects.filter(posting_id=post_id, user=request.user.id, id=comment_id)
        comment.delete()
        
        return JsonResponse({"MESSAGE":"DELETE"}, status=204)


class SearchView(View):
    def post(self, request):
        data = json.loads(request.body)

        try:
            search_word = data['search_word']
            all_posts = Post.objects.all()
            search_posts = all_posts.filter(Q(title__icontains = search_word)|Q(body__icontains = search_word))

            if search_word == "" or search_word == " " or len(search_word) >= 30:
                return JsonResponse({"message" : "WRONG_REQUEST"}, status=401)
            
            results = [
            {
                'title' : search_post.title, 
                'user'  : search_post.user.name,
                'body'  : search_post.body
            } for search_post in search_posts]

            return JsonResponse({"Result" : results}, status=200)
        except KeyError:
            return JsonResponse({"message" : "KEY_ERROR"}, status=400)
            