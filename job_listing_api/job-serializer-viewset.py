from django.utils import timezone
from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Job, Skill, Tag


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ["id", "name"]
        read_only_fields = ["id"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name"]
        read_only_fields = ["id"]


class JobSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Job
        fields = [
            "id",
            "title",
            "company",
            "location",
            "description",
            "skills",
            "tags",
            "status",
            "visibility",
            "published_at",
            "scheduled_publish_at",
            "application_deadline",
            "employment_type",
            "salary",
            "posted_by",
            "views_count",
            "applications_count",
            "priority",
            "version",
            "created_at",
            "slug",
        ]
        read_only_fields = [
            "id",
            "posted_by",
            "views_count",
            "applications_count",
            "version",
            "created_at",
            "slug",
            "original_job",
        ]
        # Excluding original_job from fields as it's handled in the viewset

    def validate_skills(self, value):
        skill_names = [item["name"] for item in value]
        existing_skills = Skill.objects.filter(name__in=skill_names)
        if len(existing_skills) != len(skill_names):
            raise serializers.ValidationError("Some skills do not exist")
        return value

    def validate_tags(self, value):
        tag_names = [item["name"] for item in value]
        existing_tags = Tag.objects.filter(name__in=tag_names)
        if len(existing_tags) != len(tag_names):
            raise serializers.ValidationError("Some tags do not exist")
        return value


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]  # Only allow POST method

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create job instance but don't save yet
        job = Job(
            title=serializer.validated_data["title"],
            company=serializer.validated_data["company"],
            location=serializer.validated_data["location"],
            description=serializer.validated_data["description"],
            status=serializer.validated_data.get("status", "draft"),
            visibility=serializer.validated_data.get("visibility", "private"),
            scheduled_publish_at=serializer.validated_data.get("scheduled_publish_at"),
            application_deadline=serializer.validated_data.get("application_deadline"),
            employment_type=serializer.validated_data.get("employment_type"),
            salary=serializer.validated_data.get("salary"),
            posted_by=request.user,
            slug=uuid.uuid4(),
        )

        # If this is a revision of an existing job
        original_job_id = request.data.get("original_job")
        if original_job_id:
            try:
                original_job = Job.objects.get(id=original_job_id)
                job.original_job = original_job
                # Get the latest version number for this job family
                latest_version = (
                    Job.objects.filter(original_job=original_job)
                    .order_by("-version")
                    .first()
                )
                job.version = (latest_version.version + 1) if latest_version else 2
            except Job.DoesNotExist:
                raise serializers.ValidationError(
                    {"original_job": "Original job does not exist"}
                )

        # Handle publication date
        if job.status == "published":
            job.published_at = timezone.now()

        job.save()

        # Handle many-to-many relationships
        skill_names = [item["name"] for item in serializer.validated_data["skills"]]
        skills = Skill.objects.filter(name__in=skill_names)
        job.skills.set(skills)

        tag_names = [item["name"] for item in serializer.validated_data["tags"]]
        tags = Tag.objects.filter(name__in=tag_names)
        job.tags.set(tags)

        # Return the serialized job
        return Response(self.get_serializer(job).data, status=status.HTTP_201_CREATED)
