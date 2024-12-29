import django_filters

from job_listing_api.models import Job, JobTypeChoice


class JobFilterset(django_filters.FilterSet):
    job_title = django_filters.CharFilter(
        field_name="job_title",
        lookup_expr="icontains",
    )
    company_name = django_filters.CharFilter(
        field_name="company_name",
        lookup_expr="icontains",
    )
    location = django_filters.CharFilter(
        field_name="company__location",
        lookup_expr="icontains",
    )
    skills = django_filters.CharFilter(
        field_name="skills__name",
        lookup_expr="iexact",
    )
    posted_by = django_filters.CharFilter(
        field_name="posted_by__id",
        lookup_expr="iexact",
    )
    created_at = django_filters.DateFromToRangeFilter(field_name="created_at")
    employment_type = django_filters.ChoiceFilter(choices=JobTypeChoice.choices)
    salary = django_filters.NumberFilter(field_name="salary", lookup_expr="icontains")

    class Meta:
        model = Job
        fields = [
            "job_title",
            "company_name",
            "company__location",
            "skills__name",
            "posted_by__id",
            "created_at",
            "salary",
            "employment_type",
        ]
