import json
from unittest import result
from django.core.exceptions import ObjectDoesNotExist

from django.http import JsonResponse

from users.decorator import login_decorator
from .models import Post, Comment
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

class PostView(View):
    @login_decorator
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

            if not Post.objects.filter(id=post_id).exists():
                return JsonResponse({"MESSAGE":"POST_DOES_NOT_EXIST"}, status=404)
            if not Comment.objects.filter(posting=post_id).exists():
                return JsonResponse({"MESSAGE":"COMMENT_DOES_NOT_EXIST"}, status=404)

            limit = int(request.GET.get("limit",3))
            offset = int(request.GET.get("offset",0))

            comments = Comment.objects.filter(posting_id=post_id, parent_comment=None)

            Result_comment = [{
            "comment_id": comment.id,
            "content" : comment.content,
            "parent_comment" : comment.parent_comment_id
            } for comment in comments]

            Result_comment = Result_comment[offset:offset+limit]

            return JsonResponse({"Result" : result, "Comment" : Result_comment}, status=200)
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