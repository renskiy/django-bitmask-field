from django import test
from django.core import exceptions

from django_bitmask_field import BitmaskField


class BitmaskFieldTestCase(test.TestCase):

    def test_bitmaskfield_cleans_valid_choice(self):
        field = BitmaskField(choices=[(1, 0), (4, 2)])
        cases = dict(
            first_choice=dict(  # 001
                choice='1',
                expected_cleaned=1,
            ),
            second_choice=dict(  # 100
                choice='4',
                expected_cleaned=4,
            ),
            combo=dict(  # 101
                choice='5',
                expected_cleaned=5,
            ),
        )
        for case, data in cases.items():
            with self.subTest(case=case):
                self.assertEqual(
                    data['expected_cleaned'],
                    field.clean(data['choice'], None),
                )

    def test_bitmaskfield_raises_error_on_invalid_choice(self):
        field = BitmaskField(choices=[(1, 0), (4, 2)])
        cases = dict(
            single_invalid_bit='2',  # 0010
            two_invalid_bits='10',  # 1010
            partly_invalid_1='3',  # 0011
            partly_invalid_2='7',  # 0111
        )
        for case, value in cases.items():
            with self.subTest(case=case):
                with self.assertRaises(exceptions.ValidationError):
                    field.clean(value, None),
