from django.db import models

from core.models import TimeStamp

class Notion(TimeStamp):
    title = models.CharField(max_length=100)
    body = models.TextField(default="")
    hit = models.PositiveIntegerField(default=0)
    user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    class Meta:
        db_table="notions"