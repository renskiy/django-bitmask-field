from django import test

from tests.models import TestModel


class BitmaskFieldTestCase(test.TestCase):

    def test(self):
        self.assertEqual(TestModel.objects.count(), 0)
