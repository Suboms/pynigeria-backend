from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated,
    IsAuthenticatedOrReadOnly,
    IsAdminUser,
)
from django.db import IntegrityError
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action
from job_api.models import Job, Skill, JobSkill
from job_api.serializers import JobSerializer
from rest_framework.exceptions import MethodNotAllowed
from django.contrib.auth.models import User

# Create your views here.


class JobViewset(viewsets.ModelViewSet):
    queryset = Job.objects.all().order_by("-created_at")
    serializer_class = JobSerializer
    permission_classes = [IsAdminUser, IsAuthenticated, IsAuthenticatedOrReadOnly]

    def list(self, request, *args, **kwargs):
        raise MethodNotAllowed(method="get")
    def create(self, request, *args, **kwargs):
        raise MethodNotAllowed(method="post")

    @action(detail=False, methods=["post"])
    def create_job(self, request, *args, **kwargs):
        # self.permission_classes = [IsAdminUser, IsAuthenticated]
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.validated_data.get("title")
        company = serializer.validated_data.get("company")
        location = serializer.validated_data.get("location")
        description = serializer.validated_data.get("description")
        posted_by = self.request.user if self.request.user.is_authenticated else ""
        skills_data = serializer.validated_data.get('skills', [])

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
            return Response({"detail":"An unexpected error occures", "error":str(e)}, status=500)
    
    
    
    

    def format_data(self, data):
        for items in data:
            if "skills" in items:
                items["skills"] = [skill["name"].title() for skill in items["skills"]]
            items.pop('id', None)

            if "posted_by" in items:
                user = User.objects.filter(id=items["posted_by"]).first()
                items["posted_by"] = user.username.title() if user else None
            
            if "title" in items:
                items["title"] = items["title"].title()

            if "company" in items:
                items["company"] = items["company"].title()

            if "location" in items:
                items["location"] = items["location"].title()

            if "description" in items:
                items["description"] = items["description"].capitalize()
        return data
    
    @action(methods=['get'], detail=False, permission_classes=[IsAuthenticatedOrReadOnly], url_path="job-list", url_name="job-list")
    def jobs_list(self,request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            modified_response = self.format_data(serializer.data)
            return self.get_paginated_response(modified_response)

        serializer = self.get_serializer(queryset, many=True)
        modified_response = self.format_data(serializer.data)
        return Response(modified_response)


