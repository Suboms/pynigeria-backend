from django.contrib.admin import ModelAdmin, register

from .models import Bookmark, Job, JobSkill, JobTag, Skill, Tag, Company, BookmarkFolder


# Register your models here.
@register(Job)
class JobAdmin(ModelAdmin):
    list_display = (
        "job_title",
        "company_name",
        "created_at",
    )
    list_filter = ("job_title", "company_name", "employment_type", "salary")
    readonly_fields = ["created_at"]


@register(Skill)
class SkillAdmin(ModelAdmin):
    list_filter = ["name"]


@register(Bookmark)
class BookmarkAdmin(ModelAdmin):
    pass
    # list_filter = [
    #     "user__email",
    #     "job__company__name",
    #     "job__company__location",
    #     "job__employment_type",
    # ]
    # list_display = [
    #     "user__email",
    #     "job__company__name",
    #     "job__company__location",
    #     "job__employment_type",
    # ]

@register(BookmarkFolder)
class BookmarkFolderAdmin(ModelAdmin):
    pass
@register(JobSkill)
class JobSkillAdmin(ModelAdmin):
    pass


@register(JobTag)
class JobTagAdmin(ModelAdmin):
    pass


@register(Tag)
class TagAdmin(ModelAdmin):
    pass


@register(Company)
class CompanyAdmin(ModelAdmin):
    pass
