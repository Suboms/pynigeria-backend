from rest_framework import serializers

from job_api.models import Job, Skill, Bookmark


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

    class Meta:
        model = Job
        exclude = ("slug",)
        read_only_fields = ["posted_by", "created_at"]


class CreateBookmarkSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bookmark
        fields = ("job",)

    # def validate_job(self, job):
    #     user = self.context['request'].user
    #     if Bookmark.objects.filter(user=user, job=job).exists():
    #         raise serializers.ValidationError("You have already bookmarked this job.")
    #     return job


class BookmarkSerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source="job.title", read_only=True)
    job_company = serializers.CharField(source="job.company", read_only=True)
    job_description = serializers.CharField(source="job.description", read_only=True)
    job_instance = serializers.HyperlinkedRelatedField(
        view_name="job-detail", lookup_field="slug", source="job", read_only=True
    )

    class Meta:
        model = Bookmark
        fields = ("job_title", "job_company", "job_description", "job_instance")
