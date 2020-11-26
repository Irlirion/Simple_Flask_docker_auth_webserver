import re

from wtforms import ValidationError


class Email(object):
    user_pattern = re.compile(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)")

    def __init__(self, message=None):
        self.message = message or "Invalid email"

    def __call__(self, form, field):
        email = field.data or ""
        if self.user_pattern.match(email) is None:
            raise ValidationError(self.message)


class Password(object):
    user_pattern = re.compile(r"^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=\S+$).{8,}$")

    def __init__(self, message=None):
        self.message = message or "Invalid password"

    def __call__(self, form, field):
        password = field.data or ""
        if self.user_pattern.match(password) is None:
            raise ValidationError(self.message)
