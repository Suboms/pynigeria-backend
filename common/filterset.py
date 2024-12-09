import django_filters

from job_api.models import Job


class JobFilterset(django_filters.FilterSet):
    title = django_filters.CharFilter(
        field_name="title",
        lookup_expr="icontains",
    )
    company = django_filters.CharFilter(
        field_name="company",
        lookup_expr="icontains",
    )
    location = django_filters.CharFilter(
        field_name="location",
        lookup_expr="icontains",
    )
    skills = django_filters.CharFilter(
        field_name="skills__name",
        lookup_expr="iexact",
    )
    posted_by = django_filters.CharFilter(
        field_name="posted_by__username",
        lookup_expr="iexact",
    )
    created_at = django_filters.DateFromToRangeFilter(field_name="created_at")

    class Meta:
        model = Job
        fields = [
            "title",
            "company",
            "location",
            "skills__name",
            "posted_by__username",
            "created_at",
        ]
