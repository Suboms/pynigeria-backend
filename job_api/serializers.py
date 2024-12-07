from rest_framework import serializers

from job_api.models import Job, JobSkill, Skill


class SkillSerializer(serializers.ModelSerializer):
    name = serializers.CharField(validators=[])

    class Meta:
        model = Skill
        fields = "__all__"


class JobSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True)

    class Meta:
        model = Job
        fields = "__all__"
        read_only_fields = ["posted_by", "created_at"]
