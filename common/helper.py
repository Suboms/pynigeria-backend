import hashlib
import random
import uuid
from datetime import datetime

from django.contrib.auth import get_user_model

User = get_user_model()


class Helper:

    def format_list(self, data):
        return self.format_data(data)

    def format_instance(self, data: dict):
        data.pop("job", None)
        instance_data = [data]
        return self.format_data(instance_data)

    def format_data(self, data: dict):
        for items in data:
            if "skills" in items:
                items["skills"] = [skill["name"].title() for skill in items["skills"]]
            items.pop("id", None)

            if "posted_by" in items:
                user = User.objects.filter(id=items["posted_by"]).first()
                items["posted_by"] = user.email.title() if user else None

            if "title" in items:
                items["title"] = items["title"].title()

            if "company" in items:
                items["company"] = items["company"].title()

            if "location" in items:
                items["location"] = items["location"].title()

            if "description" in items:
                items["description"] = items["description"].capitalize()

            if "created_at" in items:
                items["created_at"] = datetime.fromisoformat(
                    items["created_at"]
                ).strftime("%Y-%m-%d")
            if "application_deadline" in items:
                items["application_deadline"] = datetime.fromisoformat(
                    items["application_deadline"]
                ).strftime("%Y-%m-%d")
        return data

    def generate_slug(self, *args):
        input_value = []
        for arg in args:
            if isinstance(arg, list):
                for data in arg:
                    if isinstance(data, dict) and "name" in data:
                        input_value.append(data["name"].lower())
            elif isinstance(arg, (str, int)):
                input_value.append(str(arg).lower())
            else:
                input_value.append(arg)

        random.shuffle(input_value)
        combined_input = " ".join(input_value).encode("utf-8")
        seed = int(hashlib.sha256(combined_input).hexdigest(), 16)
        random.seed(seed)
        slug = uuid.UUID(int=random.getrandbits(128), version=4)
        return slug
