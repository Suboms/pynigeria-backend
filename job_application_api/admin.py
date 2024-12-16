from django.contrib.admin import register, ModelAdmin
from job_application_api.models import JobApplicationModel

# Register your models here.
@register(JobApplicationModel)
class JobApplicationAdmin(ModelAdmin):
    pass