from django.contrib.admin import register, ModelAdmin

from .models import Bookmark, Job, JobSkill, Skill


# Register your models here.
@register(Job)
class JobAdmin(ModelAdmin):
    list_display = (
        "title",
        "company",
        "location",
    )
    list_filter = (
        "title",
        "company",
        "location",
        "employment_type",
        "salary",
    )


@register(Skill)
class SkillAdmin(ModelAdmin):
    list_filter = ["name"]


@register(Bookmark)
class BookmarkAdmin(ModelAdmin):
    list_filter = [
        "user__email",
        "job__title",
        "job__company",
        "job__location",
        "job__employment_type",
    ]
    list_display = [
        "user__email",
        "job__title",
        "job__company",
        "job__location",
        "job__employment_type",
    ]


@register(JobSkill)
class JobSkillAdmin(ModelAdmin):
    pass
