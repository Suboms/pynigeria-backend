from django.conf import settings
from django.db import models

# Create your models here.


class JobTypeChoice(models.TextChoices):
    FULL_TIME = "Full Time"
    PART_TIME = "Part Time"
    CONTRACT = "Contract"
    INTERNSHIP = "Internship"
    VOLUNTARY = "Voluntary"


class Skill(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True)

    def __str__(self) -> str:
        return self.name


class Job(models.Model):
    title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField()
    skills = models.ManyToManyField(
        Skill,
        related_name="jobs",
        through="JobSkill",
        through_fields=("job", "skill"),
        db_index=True,
    )
    employment_type = models.CharField(
        max_length=255, choices=JobTypeChoice.choices, default=JobTypeChoice.FULL_TIME
    )
    application_deadline = models.DateTimeField(null=True)
    salary = models.DecimalField(max_digits=17, decimal_places=2, null=True)
    posted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    slug = models.UUIDField(unique=True, db_index=True)

    def __str__(self):
        return f"{self.title} at {self.company}"


class JobSkill(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    skill = models.ForeignKey(
        Skill, on_delete=models.CASCADE, to_field="name"
    )  # References the `name` field of Skill

    class Meta:
        unique_together = ("job", "skill")

    def __str__(self):
        return f"{self.job.title} - {self.skill.name}"


class Bookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookmarks"
    )
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name="bookmarked_by")
    note = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "job")

    def __str__(self):
        return f"{self.user.email} bookmarked this job"


