from datetime import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.utils.timezone import now

from job_listing_api.models import (
    Bookmark,
    Job,
    JobSkill,
    JobTag,
    JobTypeChoice,
    Skill,
    Tag,
    Company,
)
from common.helper import Helper
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import F

User = get_user_model()


class SkillSerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[])

    class Meta:
        model = Skill
        fields = "__all__"


class TagSerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[])

    class Meta:
        model = Tag
        fields = "__all__"


class CompanySerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[])

    class Meta:
        model = Company
        fields = "__all__"


SCHEDULE_CHOICE = {
    "Immediate": "Immediate",
    "One Week": "One Week",
    "One Month": "One Month",
    "Custom": "Custom",
}


class JobSerializer(serializers.ModelSerializer, Helper):
    job = serializers.HyperlinkedIdentityField(
        view_name="job-detail", lookup_field="slug"
    )
    skills = SkillSerializer(many=True)
    tags = TagSerializer(many=True)
    company = CompanySerializer(required=False)
    employment_type = serializers.ChoiceField(choices=JobTypeChoice.choices)

    class Meta:
        model = Job
        exclude = ("slug",)
        read_only_fields = [
            "posted_by",
            "created_at",
            "published_at",
            "views_count",
            "applications_count",
            "original_job",
            "status",
            "company_name",
            "scheduled_publish_at",
            "is_approved",
            "version",
        ]

    def to_internal_value(self, data):
        text_fields = ["employment_type", "status", "visibility", "schedule_choice"]
        for field in text_fields:
            if field in data and data[field]:
                data[field] = data[field].title()
        return super().to_internal_value(data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop("id", None)
        data = {key: val for key, val in data.items() if val is not None}
        self._format_text_field(data)
        self._format_list_fields(data)
        self._format_posted_by(data)
        self._format_date_field(data)
        self._format_salary(data)
        self._clean_company(data)

        return data

    def validate_salary(self, value):
        return value * 100

    def create(self, validated_data: dict):
        skills_data = validated_data.pop("skills", None)
        tags_data = validated_data.pop("tags", None)
        company = validated_data.pop("company", None)

        if company is not None:

            company_instance, created = Company.objects.get_or_create(
                name=company["name"].strip().lower(),
                location=company["location"].strip().lower(),
                description=company["description"].strip().lower(),
                website=company["website"].strip().lower(),
            )

            validated_data["company"] = company_instance
            if "company_name" not in validated_data:
                validated_data["company_name"] = company["name"]

        if "slug" not in validated_data:
            validated_data["slug"] = self.context.get("slug")
        if "posted_by" not in validated_data:
            validated_data["posted_by"] = self.context.get("posted_by")
        if "pubished_at" not in validated_data:
            validated_data["published_at"] = self.context.get("published_at")

        for field in ["job_title", "location", "job_description"]:
            if field in validated_data and isinstance(validated_data[field], str):
                validated_data[field] = validated_data[field].strip().lower()

        for date_field in [
            "application_deadline",
            "scheduled_publish_at",
            "published_at",
        ]:
            if date_field in validated_data:
                date_value = validated_data[date_field]
                if isinstance(date_value, datetime) and date_value.strftime(
                    "%Y-%m-%d"
                ) < now().strftime("%Y-%m-%d"):
                    raise ValidationError(
                        message={
                            date_field: f"{date_field.replace('_', ' ').capitalize()} cannot be in the past. "
                        },
                        code=400,
                    )
        with transaction.atomic():
            job_instance = Job.objects.create(**validated_data)
            for data in skills_data:
                skill_name = data["name"].strip().lower()
                skill, created = Skill.objects.get_or_create(name=skill_name)
                JobSkill.objects.create(job=job_instance, skill=skill)

            for data in tags_data:
                tag_name = data["name"].strip().lower()
                tag, created = Tag.objects.get_or_create(name=tag_name)
            JobTag.objects.create(job=job_instance, tag=tag)

        return job_instance

    def update(self, instance, validated_data):
        # Extract related fields from the validated data
        skills_data = validated_data.pop("skills", None)
        tags_data = validated_data.pop("tags", None)
        company = validated_data.pop("company", None)

        # Convert relevant fields in validated_data to lowercase
        for field in [
            "job_title",
            "company__name",
            "company__location",
            "company__description",
        ]:

            if field in validated_data:
                print(validated_data[field])
                validated_data[field] = validated_data[field].strip().lower()

        # Create a new instance as a copy of the current instance
        new_job_data = {
            field.name: getattr(instance, field.name)
            for field in instance._meta.fields
            if field.name not in ["id", "slug", "created_at"]
        }

        # Update new_job_data with validated_data
        new_job_data.update(validated_data)

        # Update the versioning details
        new_job_data["version"] = instance.version + 1
        new_job_data["original_job"] = instance
        new_job_data["slug"] = self.generate_slug()

        # Create the new job instance
        with transaction.atomic():
            
            new_instance = Job.objects.create(**new_job_data)

            # Update Many-to-Many fields (skills and tags)
            if skills_data is not None:
                skills_instances = []
                for skill in skills_data:
                    skill_instance, _ = Skill.objects.get_or_create(
                        name=skill["name"].strip().lower()
                    )
                    JobSkill.objects.get_or_create(
                        job=new_instance, skill=skill_instance
                    )
                    skills_instances.append(skill_instance)
                new_instance.skills.set(skills_instances)

            if tags_data is not None:
                tags_instances = []
                for tag in tags_data:
                    tag_instance, _ = Tag.objects.get_or_create(
                        name=tag["name"].strip().lower()
                    )
                    JobTag.objects.get_or_create(job=new_instance, tag=tag_instance)
                    tags_instances.append(tag_instance)
                new_instance.tags.set(tags_instances)

            new_instance.save()

        return new_instance


class CreateBookmarkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bookmark
        fields = (
            "job",
            "note",
        )


class BookmarkSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.title", read_only=True)
    job_company = serializers.CharField(source="job.company", read_only=True)
    job_description = serializers.CharField(source="job.description", read_only=True)
    job_instance = serializers.HyperlinkedRelatedField(
        view_name="job-detail", lookup_field="slug", source="job", read_only=True
    )

    class Meta:
        model = Bookmark
        fields = ("job_title", "job_company", "job_description", "job_instance", "note")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if data.get("note") is None:
            data.pop("note", None)
        return data


class JobApproveSerializer(serializers.Serializer):
    is_approved = serializers.BooleanField()
    message = serializers.CharField(required=False)

    def save(self, job_instance, **kwargs):
        job_instance.is_approved = self.validated_data["is_approved"]
        if job_instance.is_approved is True:
            job_instance.status = "Published"
            job_instance.published_at = now()
        else:
            job_instance.status = "Draft"
            job_instance.published_at = None
        job_instance.save()
        return job_instance
