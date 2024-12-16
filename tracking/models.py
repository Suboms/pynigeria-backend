from django.db import models
from django.contrib.auth import User
# Create your models here.

class UserActivity(models.Model):
	user = models.OneToOneField(User,related_name='activity', on_delete=models.CASCADE)
	eviction_status = models.BooleanField(default=False)

	def __init__(self):
		return f"{self.user} Activity"


class Message(models.Model):
	user = models.ForeignKey(UserActivity,on_delete=models.CASCADE,related_name="messages")
	total_message = models.IntegerField(default=0)

	def __init__(self):
		return f"{self.user.user} Messages"
