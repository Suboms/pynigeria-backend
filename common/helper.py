import hashlib
import random
import uuid
from datetime import datetime
from decimal import Decimal

from django.contrib.auth import get_user_model

User = get_user_model()


class Helper:

    def generate_slug(self):
        # Generate initial UUID
        initial_uuid = uuid.uuid4()

        # Convert UUID to bytes and hash it
        hash_obj = hashlib.sha256(str(initial_uuid).encode())
        hash_bytes = hash_obj.digest()

        # Use the first 16 bytes of the hash to create a new UUID (version 3)
        new_uuid = uuid.UUID(bytes=hash_bytes[:16], version=4)

        return new_uuid

    def _format_list_fields(self, data):
        for field in ["job_skills"]:
            if field in data and data[field]:
                for items in data[field]:
                    if "skill" in items and items["skill"] is not None:
                        items["skill"] = {"name": items["skill"]["name"].title()}
                # data[field] = 

    def _format_posted_by(self, data):
        if "posted_by" in data:
            user = User.objects.filter(id=data["posted_by"]).first()
            data["posted_by"] = user.email.title() if user else None

    def _format_text_field(self, data):
        for field in ["job_title", "job_description"]:
            if field in data and data[field]:
                data[field] = data[field].title()

            if "job_description" in data and data["job_description"]:
                data["job_description"] = data["job_description"].capitalize()

    def _format_date_field(self, data):
        for field in [
            "created_at",
            "application_deadline",
            "scheduled_publish_at",
            "published_at",
        ]:
            if field in data and data[field]:
                try:
                    data[field] = datetime.fromisoformat(data[field]).strftime(
                        "%Y-%m-%d"
                    )
                except (ValueError, TypeError):
                    # Fallback to original value if parsing fails
                    pass

    def _format_salary(self, data):
        salary = Decimal(data.get("salary", 0))
        if "salary" in data and data["salary"]:
            data["salary"] = str(salary / 100)
