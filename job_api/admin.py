from django.contrib import admin
from .models import Skill, Job, Bookmark, JobSkill

# Register your models here.

admin.site.register(Skill)
admin.site.register(Job)
admin.site.register(JobSkill)
admin.site.register(Bookmark)