from django.urls import path
from notionboards.views import ListView, PostView, CommentView
urlpatterns = [
    path("/list", ListView.as_view()),
    path("/detail/<int:post_id>", PostView.as_view()),
    path('/<int:post_id>/comments', CommentView.as_view()),
]
