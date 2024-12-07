from django.contrib.auth.models import User
from django.db.models import Q
from django.db.transaction import atomic
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response

from common.filterset import JobFilterset
from common.helper import Helper
from job_api.models import Job, JobSkill, Skill
from job_api.serializers import JobSerializer

# Create your views here.


class JobViewset(viewsets.ModelViewSet, Helper):
    queryset = Job.objects.all().order_by("-created_at")
    serializer_class = JobSerializer
    permission_classes = [IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["skills__name", "title", "company", "location"]
    ordering_fields = ["skills__name", "title", "company", "location", "posted_by__username"]
    ordering = ["title"]
    filterset_class = JobFilterset

    def list(self, request, *args, **kwargs):
        raise MethodNotAllowed(method="get")

    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed(method="post")

    with atomic():

        @action(detail=False, methods=["post"])
        def create_job(self, request, *args, **kwargs):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            title = serializer.validated_data.get("title")
            company = serializer.validated_data.get("company")
            location = serializer.validated_data.get("location")
            description = serializer.validated_data.get("description")
            posted_by = self.request.user if self.request.user.is_authenticated else ""
            skills_data = serializer.validated_data.get("skills", [])

            try:

                job = Job(
                    title=title.lower(),
                    company=company.lower(),
                    location=location.lower(),
                    description=description.lower(),
                    posted_by=posted_by,
                )
                job.save()

                for data in skills_data:
                    skill_name = data["name"].strip().lower()
                    skill, created = Skill.objects.get_or_create(name=skill_name)
                    JobSkill.objects.create(job=job, skill=skill)

                job_serializer = self.get_serializer(job)

                return Response(job_serializer.data, status=201)
            except Exception as e:
                return Response(
                    {"detail": "An unexpected error occures", "error": str(e)},
                    status=500,
                )

    @action(
        methods=["get"],
        detail=False,
        permission_classes=[IsAuthenticatedOrReadOnly],
        url_path="job-list",
        url_name="job-list",
    )
    def jobs_list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            modified_response = self.format_data(serializer.data)
            return self.get_paginated_response(modified_response)

        serializer = self.get_serializer(queryset, many=True)
        modified_response = self.format_data(serializer.data)
        return Response(modified_response)

    def filter_queryset(self, queryset):
        search_param = self.request.query_params.get("search")

        if search_param:
            search_terms = [
                term.strip().lower() for term in search_param.split(",") if term.strip()
            ]
            skill_filter = Q()
            for term in search_terms:
                skill_filter |= (
                    Q(skills__name__iexact=term)
                    | Q(title__icontains=term)
                    | Q(company__icontains=term)
                    | Q(location__icontains=term)
                )
            # Apply the filter to the queryset
            queryset = self.queryset.filter(skill_filter).distinct()

        # Return the filtered queryset
        return super().filter_queryset(queryset)
