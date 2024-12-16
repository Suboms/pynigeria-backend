from django.db import models
from django.utils.text import slugify


class JobPosting(models.Model):
    JOB_TYPES = [
        ('FT', 'Full-Time'),
        ('PT', 'Part-Time'),
        ('CT', 'Contract'),
        ('IN', 'Internship'),
        ('FR', 'Freelance'),
    ]

    # we can track who posted the job in the feature
    # posted_by = models.ForeignKey(User, on_delete=models.DO_NOTHING)

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, max_length=255, blank=True,)
    company_name = models.CharField(max_length=255)
    description = models.TextField()
    location = models.CharField(max_length=255)  # Could be city, state, country
    job_type = models.CharField(max_length=2, choices=JOB_TYPES, default='FT')
    skills_required = models.TextField(help_text="Comma-separated list of skills")
    posted_date = models.DateTimeField(auto_now_add=True)
    last_date_to_apply = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} at {self.company_name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
