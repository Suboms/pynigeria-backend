from rest_framework import serializers

from job_listing_api.models import Bookmark, Job, JobTypeChoice, Skill
from datetime import datetime

from django.contrib.auth import get_user_model
from decimal import Decimal

User = get_user_model()
class SkillSerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[])

    class Meta:
        model = Skill
        fields = "__all__"


class JobSerializer(serializers.ModelSerializer):
    job = serializers.HyperlinkedIdentityField(
        view_name="job-detail", lookup_field="slug"
    )
    skills = SkillSerializer(many=True)

    employment_type = serializers.ChoiceField(choices=JobTypeChoice.choices)

    class Meta:
        model = Job
        exclude = ("slug",)
        read_only_fields = ["posted_by", "created_at"]

    def to_internal_value(self, data):
        data["employment_type"] = data["employment_type"].title()
        return super().to_internal_value(data)
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Handle skills
        if "skills" in data and data["skills"]:
            data["skills"] = [{"name":skill["name"].title()} for skill in data["skills"]]
        
        # Remove ID field
        data.pop("id", None)
        
        # Format posted by field
        if "posted_by" in data:
            user = User.objects.filter(id=data["posted_by"]).first()
            data["posted_by"] = user.email.title() if user else None
        
        # Capitalize and format text fields
        text_fields = ["title", "company", "location"]
        for field in text_fields:
            if field in data and data[field]:
                data[field] = data[field].title()
        
        # Capitalize description
        if "description" in data and data["description"]:
            data["description"] = data["description"].capitalize()
        
        # Format date fields
        date_fields = ["created_at", "application_deadline"]
        for field in date_fields:
            if field in data and data[field]:
                try:
                    data[field] = datetime.fromisoformat(data[field]).strftime("%Y-%m-%d")
                except (ValueError, TypeError):
                    # Fallback to original value if parsing fails
                    pass

        salary = Decimal(data.get("salary", 0))
        if "salary" in data and data["salary"]:
            data["salary"] = str(salary / 100)
        return data
        

    def validate_salary(self, value):
        return value*100
    
    def update(self, instance, validated_data):
        skills_data = validated_data.pop("skills", None)
        # salary = validated_data.pop("salary", None)
        if skills_data is not None:
            skills_instance = []
            for skill in skills_data:
                skill_instance, created = Skill.objects.get_or_create(name=skill["name"].strip().lower())
                skills_instance.append(skill_instance)
            instance.skills.set(skills_instance)
        instance.salary = instance.salary
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
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
