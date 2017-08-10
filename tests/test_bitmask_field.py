from django import test
from django.core import exceptions, checks

from django_bitmask_field import BitmaskField

from .models import TestModel, ContributingModel


class BitmaskFieldTestCase(test.TestCase):

    def test_bitmask_return_error_on_choices_overflow(self):
        cases = dict(
            bitmask=dict(
                field=BitmaskField(),
                last_bit=2147483648,
            ),
        )

    def test_bitmaskfield_cleans_valid_choice(self):
        field = BitmaskField(choices=[(1, 'choice 0'), (4, 'choice 1')])
        cases = dict(
            first_choice=dict(  # 0001
                choice=1,
                expected_cleaned=1,
            ),
            second_choice=dict(  # 0100
                choice=4,
                expected_cleaned=4,
            ),
            combo=dict(  # 0101
                choice=5,
                expected_cleaned=5,
            ),
        )
        for case, data in cases.items():
            with self.subTest(case=case):
                self.assertEqual(
                    data['expected_cleaned'],
                    field.clean(data['choice'], None),
                )

    def test_bitmaskfield_works_with_multibit_choices(self):
        field = BitmaskField(choices=[(1, 'choice 0'), (4, 'choice 1'), (5, 'choice 2')])
        self.assertEqual(5, field.clean(5, None))

    def test_bitmaskfield_raises_error_on_invalid_choice(self):
        field = BitmaskField(choices=[(1, 'choice 0'), (4, 'choice 1')])
        cases = dict(
            single_invalid_bit=2,  # 0010
            two_invalid_bits=10,  # 1010
            partly_invalid_1=3,  # 0011
            partly_invalid_2=6,  # 0110
            partly_invalid_3=7,  # 0111
        )
        for case, value in cases.items():
            with self.subTest(case=case):
                with self.assertRaises(exceptions.ValidationError):
                    field.clean(value, None),

    def test_bitmaskfield_write_and_read_from_db(self):
        test_model = TestModel(bitmask=5)
        test_model.save()
        self.assertEqual(5, TestModel.objects.first().bitmask)

    # TODO test optgroup choices
    # TODO test last bit of all bitmask fields
    # TODO check choices validation
