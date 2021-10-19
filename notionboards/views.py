import json
from unittest import result
from django.core.exceptions import ObjectDoesNotExist

from django.http import JsonResponse

from users.decorator import login_decorator
from .models import Notion
from django.views import View

class ListView(View):
    def get(self, request):
        page       = request.GET.get("page", 1)
        page       = int(page or 1)
        page_size  = 10
        limit      = page_size * page 
        offset     = limit - page_size
        
        notions = Notion.objects.all().order_by('-id')
        
        if not notions [offset:limit]:
            return JsonResponse({"message" : "PAGE_NOT_FOUND"}, status=404)
        
        result = [{
            "count" : len(notions)-(offset+i),
            "title" : notion.title,
            "hit" : notion.hit,
            "body" : notion.body,
            "nickname" : notion.user.nickname
        } for i,notion in enumerate(notions [offset:limit])]
        
        return JsonResponse({"Result" : result, "page" : page}, status=200)

    @login_decorator
    def post(self, request):
        data = json.loads(request.body)
        user = request.user

        try:
            result=Notion.objects.create(
                title = data['title'],
                body = data['body'],
                user_id = user.id
            )
            return JsonResponse({"message" : "SUCCESS"}, status=201)
        except KeyError:
            return JsonResponse({"message" : "KEY_ERROR"}, status=400)

class NotionView(View):
    def get(self, request):
        notion_id = request.GET.get("id")

        try:
            notion = Notion.objects.get(id=notion_id)
            
            notion.hit += 1
            notion.save()
            
            result = {
                "title" : notion.title,
                "body" : notion.body,
                "hit" : notion.hit,
                "create_at" : notion.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                "update_at" : notion.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                "nickname" : notion.user.nickname
            }
            return JsonResponse({"Result" : result}, status=200)
        except Notion.DoesNotExist:
            return JsonResponse({"message" : "NOTIONS_NOT_FOUND"}, status=404)

    @login_decorator
    def put(self, request):
        data = json.loads(request.body)
        notion_id = request.GET.get("id")
        user = request.user
        try:
            notion = Notion.objects.get(id=notion_id)
            
            if not (notion.user_id == user.id):
                return JsonResponse({"message" : "NO_PERMISSION"}, status=401)
            
            notion.title = data["title"]
            notion.body = data["body"]
            notion.save()

            return JsonResponse({"message" : "SUCCESS"}, status=201)
        except KeyError:
            return JsonResponse({"message" : "KEY_ERROR"}, status=400)
        except Notion.DoesNotExist:
            return JsonResponse({"message" : "NOTION_NOT_FOUND"}, status=404)
    
    @login_decorator
    def delete(self, request):
        notion_id = request.GET.get('id')
        user = request.user

        try:
            notion = Notion.objects.get(id=notion_id)
            
            if notion.user_id != user.id:
                return JsonResponse({"message" : "NO_PERMISSION"}, status=401)
            
            notion.delete()
            
            return JsonResponse({'message': 'NOTION_DELETED'}, status=200)
        
        except ObjectDoesNotExist:
            return JsonResponse({'message': 'NOTION_DOES_NOT_EXIST'}, status=404)