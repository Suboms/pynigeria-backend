from django.db import models
from django.conf import settings

# Create your models here.


class ApplicationStatus(models.TextChoices):
    PENDING = "Pending"
    REVIEWED = "Reviewed"
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"


class JobApplicationModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications"
    )
    job = models.ForeignKey(
        "job_listing_api.Job", on_delete=models.CASCADE, related_name="applications"
    )
    resume = models.FileField(upload_to="resumes/", null=True, blank=True)
    github_url = models.URLField(blank=True, null=True)
    portfolio_url = models.URLField(blank=True, null=True)
    linkedin_url = models.URLField(blank=True, null=True)
    status = models.CharField(
        max_length=50,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING,
    )  # Example statuses: Pending, Accepted, Rejected
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Job Applications"
