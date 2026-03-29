from django.test import TestCase


class SampleTestCase(TestCase):
    def test_sample(self) -> None:
        self.assertEqual(1 + 1, 2)
