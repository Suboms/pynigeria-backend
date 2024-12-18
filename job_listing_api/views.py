from django.db.models import Q
from django.db.transaction import atomic
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.authentication import SessionAuthentication
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from common.filterset import JobFilterset
from common.helper import Helper
from job_listing_api.models import Bookmark, Job, JobSkill, Skill
from job_listing_api.serializers import (
    BookmarkSerializer,
    CreateBookmarkSerializer,
    JobSerializer,
)
from .permissions import IsJobPoster
from rest_framework import status

# Create your views here.


class JobViewset(viewsets.ModelViewSet, Helper):
    queryset = Job.objects.all().order_by("-created_at")
    serializer_class = JobSerializer
    authentication_classes = [SessionAuthentication, JWTAuthentication]
    permission_classes = [IsJobPoster]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = [
        "skills__name",
        "title",
        "company",
        "location",
        "employment_type",
        "salary",
    ]
    ordering_fields = [
        "skills__name",
        "title",
        "company",
        "location",
        "posted_by__email",
        "employment_type",
        "salary",
    ]
    ordering = ["title"]
    filterset_class = JobFilterset
    lookup_field = "slug"

    def list(self, request, *args, **kwargs):
        raise MethodNotAllowed(method="get")

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
            queryset = self.queryset.filter(skill_filter).distinct()

        return super().filter_queryset(queryset)

    @atomic()
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.validated_data.get("title")
        company = serializer.validated_data.get("company")
        location = serializer.validated_data.get("location")
        description = serializer.validated_data.get("description")
        job_type = serializer.validated_data.get("employment_type")
        salary = serializer.validated_data.get("salary")
        deadline = serializer.validated_data.get("application_deadline")
        posted_by = self.request.user if self.request.user.is_authenticated else ""
        skills_data = serializer.validated_data.get("skills", [])
        slug = self.generate_slug(
            title,
            company,
            location,
            description,
            str(posted_by.id),
            skills_data,
            job_type,
            str(salary),
            str(deadline),
        )

        job = Job(
            title=title.lower(),
            company=company.lower(),
            location=location.lower(),
            description=description.lower(),
            posted_by=posted_by,
            salary=salary,
            employment_type=job_type,
            application_deadline=deadline,
            slug=slug,
        )
        job.save()

        for data in skills_data:
            skill_name = data["name"].strip().lower()
            skill, created = Skill.objects.get_or_create(name=skill_name)
            JobSkill.objects.create(job=job, skill=skill)

        job_serializer = self.get_serializer(job)

        return Response(job_serializer.data, status=201)

    @action(
        methods=["get"],
        detail=False,
        url_path="job-list",
        url_name="job-list",
    )
    def job_list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @atomic()
    def update(self, request, *args, **kwargs):
        """
        Custom update method with enhanced validation for nested fields.

        Supports partial and full updates with comprehensive data handling.
        """
        # Retrieve the existing instance
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        self.check_object_permissions(request, instance)
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
            context={"request": request},  # Important for nested serializers
        )
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()

        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = None
        return Response(
            self.get_serializer(updated_instance).data, status=status.HTTP_200_OK
        )

    @atomic()
    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    @atomic()
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=204)


class BookmarkViewset(viewsets.ModelViewSet):

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # User-specific bookmarks
        return Bookmark.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return CreateBookmarkSerializer
        return BookmarkSerializer

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed(method="patch")

    def update(self, request, *args, **kwargs):
        raise MethodNotAllowed(method="put")

    @atomic()
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        job = serializer.validated_data.get("job")
        user = request.user
        bookmark = Bookmark(job=job, user=user)
        bookmark.save()
        return Response({"message": "Job bookmarked successfully"}, status=200)
