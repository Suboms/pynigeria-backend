from rest_framework import serializers

from job_api.models import Bookmark, Job, JobTypeChoice, Skill


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
