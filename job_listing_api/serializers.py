from datetime import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.timezone import now
from rest_framework import serializers
from taggit.serializers import TaggitSerializer, TagListSerializerField

from common.helper import Helper
from job_listing_api.models import (
    Bookmark,
    BookmarkFolder,
    Company,
    Job,
    JobSkill,
    JobTypeChoice,
    Skill,
)

User = get_user_model()


class SkillSerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[])

    class Meta:
        model = Skill
        fields = "__all__"


class JobSkillSerializer(serializers.ModelSerializer):
    skill = SkillSerializer()

    class Meta:
        model = JobSkill
        exclude = (
            "id",
            "job",
        )
    def to_internal_value(self, data):
        text_fields = ["skill_level"]
        for field in text_fields:
            if field in data and data[field]:
                data[field] = data[field].title()
        return super().to_internal_value(data)

class JobSerializer(TaggitSerializer, serializers.ModelSerializer, Helper):
    job = serializers.HyperlinkedIdentityField(
        view_name="job-detail", lookup_field="slug"
    )
    job_skills = JobSkillSerializer(many=True)
    tags = TagListSerializerField()

    employment_type = serializers.ChoiceField(choices=JobTypeChoice.choices)
    company_name = serializers.CharField(required=False)

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
            "scheduled_publish_at",
            "is_approved",
            "version",
        ]

    def to_internal_value(self, data):
        text_fields = ["employment_type", "status", "visibility"]
        for field in text_fields:
            if field in data and data[field]:
                data[field] = data[field].title()
        return super().to_internal_value(data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data.pop("id", None)
        data.pop("skills", None)
        self._format_text_field(data)
        self._format_list_fields(data)
        self._format_posted_by(data)
        self._format_date_field(data)
        self._format_salary(data)

        return data

    def validate(self, attrs):
        if "salary" in attrs:
            attrs["salary"] = attrs["salary"] * 100

        for date_field in [
            "application_deadline",
            "published_at",
        ]:
            if date_field in attrs:
                date_value = attrs[date_field]
                if isinstance(date_value, datetime) and date_value.strftime(
                    "%Y-%m-%d"
                ) < now().strftime("%Y-%m-%d"):
                    raise ValidationError(
                        message={
                            date_field: f"{date_field.replace('_', ' ').capitalize()} cannot be in the past. "
                        },
                        code=400,
                    )
        for field in ["job_title", "job_description"]:
            if field in attrs and isinstance(attrs[field], str):
                attrs[field] = attrs[field].strip().lower()

        if "company" in attrs and attrs["company"] is not None:
            attrs["company"] = attrs.get("company")
            attrs["company_name"] = attrs.get("company").name.strip().lower()
        else:
            attrs["company"] = attrs.get("company")
            attrs["company_name"] = (
                attrs.get("company_name").strip().lower()
                if attrs.get("company_name")
                else None
            )

        return super().validate(attrs)

    def create(self, validated_data):
        skills_data = validated_data.pop("job_skills", None)
        tags_data = validated_data.pop("tags", None)

        if "slug" not in validated_data:
            validated_data["slug"] = self.context.get("slug")
        if "posted_by" not in validated_data:
            validated_data["posted_by"] = self.context.get("posted_by")
        if "pubished_at" not in validated_data:
            validated_data["published_at"] = None

        with transaction.atomic():
            job_instance = Job.objects.create(**validated_data)

            for data in skills_data:
                skill_data = data['skill']
                skill_instance, created = Skill.objects.get_or_create(name=skill_data['name'].strip().lower())
            
                # Create JobSkill instance and associate with Job
                JobSkill.objects.create(
                    job=job_instance,
                    skill=skill_instance,
                    skill_level=data['skill_level']
                )
            if tags_data is not None:
                job_instance.tags.add(*[data.strip().lower() for data in tags_data])

        return job_instance

    def update(self, instance, validated_data):
        # Extract related fields from the validated data
        skills_data = validated_data.pop("job_skills", None)
        tags_data = validated_data.pop("tags", "[]")

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
                for items in skills_data:
                    if "skill" in items and items["skill"] is not None:
                        skill_instance, _ = Skill.objects.get_or_create(
                            name=items["skill"]["name"].strip().lower()
                        )
                    JobSkill.objects.get_or_create(
                        job=new_instance, skill=skill_instance, skill_level=items['skill_level']
                    )
                    skills_instances.append(skill_instance)
                new_instance.skills.set(skills_instances)

            if tags_data is not None:
                new_instance.tags.add(*[data.strip().lower() for data in tags_data])

            new_instance.save()

        return new_instance


class JobApproveSerializer(serializers.Serializer):
    is_approved = serializers.BooleanField()
    message = serializers.CharField(required=False)

    def save(self, job_instance, **kwargs):
        job_instance.is_approved = self.validated_data["is_approved"]
        job_instance.save()
        return job_instance


class BookmarkFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookmarkFolder
        exclude = ("user",)

    def validate(self, attrs):
        if "name" in attrs:
            attrs["name"] = attrs["name"].strip().lower()

        if "description" in attrs:
            attrs["description"] = attrs["description"].strip().lower()
        return super().validate(attrs)

    def create(self, validated_data: dict):

        if "user" not in validated_data:
            validated_data["user"] = self.context.get("request").user

        with transaction.atomic():
            folder_instance, created = BookmarkFolder.objects.get_or_create(
                **validated_data
            )
        return folder_instance


class BookmarkSerializer(serializers.ModelSerializer):
    job_instance = serializers.HyperlinkedRelatedField(
        view_name="job-detail", lookup_field="slug",source="job", read_only=True
    )
    class OverrideQuery(serializers.HyperlinkedRelatedField):

        def get_queryset(self):
            request = self.context.get("request")
            if request and hasattr(request, "user"):
                return BookmarkFolder.objects.filter(user=request.user)
            return BookmarkFolder.objects.none()
    
    folder = OverrideQuery(view_name="bookmarkfolder-detail", lookup_field="pk")
        

    class Meta:
        model = Bookmark
        fields = "__all__"

    def create(self, validated_data: dict):

        if "user" not in validated_data:
            validated_data["user"] = self.context.get("request").user

        with transaction.atomic():
            bookmark_instance, created = Bookmark.objects.get_or_create(
                **validated_data
            )
        return bookmark_instance


    

    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     if data.get("note") is None:
    #         data.pop("note", None)
    #     return data


class CompanySerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[])

    class Meta:
        model = Company
        fields = "__all__"
