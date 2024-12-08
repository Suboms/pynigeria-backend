from django.contrib.auth.models import User
from typing import Dict


class Helper:

    def format_list(self, data):
        return self.format_data(data)
    
    def format_instance(self, data:dict):
        data.pop("job",None)
        instance_data = [data]
        return self.format_data(instance_data)

    def format_data(self, data:dict):
        for items in data:
            if "skills" in items:
                items["skills"] = [skill["name"].title() for skill in items["skills"]]
            items.pop("id", None)

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
