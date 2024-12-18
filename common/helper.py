import hashlib
import random
import uuid
from datetime import datetime

from django.contrib.auth import get_user_model

User = get_user_model()


class Helper:


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
