from django.db import models
from core.models import TimeStamp

class Post(TimeStamp):
    title    = models.CharField(max_length=100)
    body     = models.TextField(default="")
    hit      = models.PositiveIntegerField(default=0)
    user     = models.ForeignKey("users.User", on_delete=models.CASCADE)
    category = models.ForeignKey("Category", on_delete=models.CASCADE)
    
    class Meta:
        db_table="posts"

class Comment(TimeStamp):
    content        = models.CharField(max_length=500)
    user           = models.ForeignKey('users.User', on_delete=models.CASCADE)
    posting        = models.ForeignKey('Post', on_delete=models.CASCADE)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'comments'

class Category(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        db_table="categories"
