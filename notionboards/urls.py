from django.urls import path
from notionboards.views import ListView, NotionView

urlpatterns = [
    path("/list", ListView.as_view()),
    path("/detail", NotionView.as_view()),
]
