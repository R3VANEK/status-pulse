from django.test import SimpleTestCase

from accounts.domain.exceptions import InvalidEmail
from accounts.domain.value_objects import Email


class EmailTests(SimpleTestCase):
    def test_normalizes_case_and_whitespace(self) -> None:
        email = Email("  Jan.Kowalski@Example.COM ")
        self.assertEqual(email.value, "jan.kowalski@example.com")

    def test_equal_when_values_equal(self) -> None:
        self.assertEqual(Email("jan@example.com"), Email("JAN@example.com"))

    def test_rejects_invalid_addresses(self) -> None:
        for invalid in [
            "",
            "jan",
            "jan@",
            "@example.com",
            "jan@example",
            "jan kowalski@example.com",
        ]:
            with self.subTest(invalid=invalid):
                with self.assertRaises(InvalidEmail):
                    Email(invalid)

    def test_is_immutable(self) -> None:
        email = Email("jan@example.com")
        with self.assertRaises(AttributeError):
            email.value = "other@example.com"  # type: ignore[misc]
