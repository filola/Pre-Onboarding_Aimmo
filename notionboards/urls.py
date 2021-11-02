from django.urls import path
from notionboards.views import ListView, PostView

urlpatterns = [
    path("/list", ListView.as_view()),
    path("/detail", PostView.as_view())
]
