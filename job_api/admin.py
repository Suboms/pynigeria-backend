from django.contrib import admin

from .models import Bookmark, Job, JobSkill, Skill


# Register your models here.
class JobAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "company",
        "location",
    )


admin.site.register(Skill)
admin.site.register(Job, JobAdmin)
admin.site.register(JobSkill)
admin.site.register(Bookmark)
