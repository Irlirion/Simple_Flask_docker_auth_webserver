from unittest import TestCase
from unittest.mock import patch

from wtforms.validators import ValidationError

from resources.validators import Email, Password


class TestEmail(TestCase):
    def setUp(self) -> None:
        self.email_validator = Email()

    @patch('wtforms.StringField')
    def test_call_error(self, MockStringField):
        field = MockStringField()
        field.data = ""
        with self.subTest("invalid"):
            self.assertRaises(ValidationError, lambda: self.email_validator(None, field))

    @patch('wtforms.StringField')
    def test_call(self, MockStringField):
        field = MockStringField()
        field.data = "e@a.tu"

        self.assertIsNone(self.email_validator(None, field))


class TestPassword(TestCase):
    def setUp(self) -> None:
        self.password_validator = Password()

    @patch('wtforms.PasswordField')
    def test_call_error(self, MockPasswordField):
        field = MockPasswordField()
        field.data = "asdasdasd"

        self.assertRaises(ValidationError, lambda: self.password_validator(None, field))

    @patch('wtforms.StringField')
    def test_call(self, MockPasswordField):
        field = MockPasswordField()
        field.data = "aA1@qwert"

        self.assertIsNone(self.password_validator(None, field))
