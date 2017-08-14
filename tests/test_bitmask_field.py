import unittest2

from django import test
from django.core import exceptions, serializers

from django_bitmask_field import BitmaskField, BitmaskFormField

from .models import TestModel, ContributingModel, TestForm


class TestCase(test.TestCase, unittest2.TestCase):
    pass


class BitmaskFieldTestCase(TestCase):

    def test_bitmaskfield_return_error_on_invalid_choices(self):
        cases = dict(
            none=[(None, 'choice')],
            str=[('foo', 'choice')],
            negative=[(-1, 'choice')],
            optgroup=[('optgroup', [(None, 'choice')])],
        )
        for case, choices in cases.items():
            with self.subTest(case=case):
                field = BitmaskField(choices=choices)
                field.contribute_to_class(ContributingModel, 'bitmask')
                errors = field.check()
                self.assertEqual(1, len(errors))
                error = errors[0]
                self.assertEqual("all 'choices' must be of integer type.", error.msg)

    def test_bitmaskfield_max_length_validation(self):
        field = BitmaskField(max_length=1)
        field.clean(256, None)
        with self.assertRaises(exceptions.ValidationError):
            field.clean(257, None)

    def test_bitmaskfield_cleans_valid_choice(self):
        field = BitmaskField(choices=[(1, 'choice 0'), ('optgroup', [(4, 'choice 1')])])
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
        field = BitmaskField(choices=[(1, 'choice 0'), (4, 'choice 1'), ('optgroup', [(5, 'choice 2')])])
        self.assertEqual(5, field.clean(5, None))

    def test_bitmaskfield_raises_error_on_invalid_choice(self):
        field = BitmaskField(choices=[(1, 'choice 0'), ('optgroup', [(4, 'choice 1')])])
        cases = dict(
            none=None,
            single_invalid_bit=2,  # 0010
            two_invalid_bits=10,  # 1010
            partly_invalid_1=3,  # 0011
            partly_invalid_2=6,  # 0110
            partly_invalid_3=7,  # 0111
        )
        for case, value in cases.items():
            with self.subTest(case=case):
                with self.assertRaises(exceptions.ValidationError):
                    field.clean(value, None)

    def test_bitmaskfield_write_and_read_from_db(self):
        cases = dict(
            empty=0,
            single=1,
            double=5,
            null=None,
        )
        for case, value in cases.items():
            with self.subTest(case=case):
                test_model = TestModel(bitmask=value)
                test_model.save()
                self.assertEqual(value, TestModel.objects.get(id=test_model.id).bitmask)

    def test_bitmaskfield_serialization_deserialization(self):
        cases = dict(
            none=None,
            regualar=42,
        )
        for case, expected_value in cases.items():
            with self.subTest(case=case):
                model = TestModel(bitmask=expected_value)
                serialized_data = serializers.serialize("xml", [model])
                deserialized_data = list(serializers.deserialize('xml', serialized_data))
                deserialized_model = deserialized_data[0].object
                self.assertEqual(expected_value, deserialized_model.bitmask)


class BitmaskFormFieldTestCase(TestCase):

    def test_is_valid(self):
        cases = dict(
            empty=dict(
                data={},
                is_valid=False,
                errors={'bitmask', 'bitmask_int'},
                expected={},
            ),
            blank=dict(
                data={'bitmask': [], 'bitmask_int': ''},
                is_valid=False,
                errors={'bitmask', 'bitmask_int'},
                expected={},
            ),
            regular=dict(
                data={'bitmask': ['1'], 'bitmask_int': '42'},
                is_valid=True,
                errors=set(),
                expected={'bitmask': 1, 'bitmask_int': 42},
            ),
        )
        for case, test_data in cases.items():
            with self.subTest(case=case):
                form = TestForm(test_data['data'])
                self.assertEqual(
                    test_data['is_valid'],
                    form.is_valid(),
                    form.errors.as_text(),
                )
                self.assertFalse(test_data['errors'] ^ set(form.errors))
                self.assertEqual(test_data['expected'], form.cleaned_data)

    def test_has_changed(self):
        cases = dict(
            empty=dict(
                initial=None,
                data={},
                has_changed=False,
            ),
            scratch=dict(
                initial=None,
                data={'bitmask': ['1'], 'bitmask_int': '42'},
                has_changed=True,
            ),
            changed=dict(
                initial={'bitmask': 1, 'bitmask_int': 42},
                data={'bitmask': ['1', '4'], 'bitmask_int': '42'},
                has_changed=True,
            ),
            not_changed=dict(
                initial={'bitmask': 1, 'bitmask_int': 42},
                data={'bitmask': ['1'], 'bitmask_int': '42'},
                has_changed=False,
            ),
        )
        for case, test_data in cases.items():
            with self.subTest(case=case):
                form = TestForm(test_data['data'], initial=test_data['initial'])
                self.assertEqual(test_data['has_changed'], form.has_changed())

    def test_prepare_value(self):
        cases = dict(
            none=dict(
                initial_value=None,
                prepared_value=None,
            ),
            zero=dict(
                initial_value=0,
                prepared_value=0,
            ),
            prepared=dict(
                initial_value=['1', '4'],
                prepared_value=['1', '4'],
            ),
            single_value=dict(
                initial_value=32,
                prepared_value=[32],
            ),
            double_value=dict(
                initial_value=33,
                prepared_value=[1, 32],
            ),
        )
        for case, test_data in cases.items():
            with self.subTest(case=case):
                form_field = BitmaskFormField()
                self.assertEqual(
                    test_data['prepared_value'],
                    form_field.prepare_value(test_data['initial_value']),
                )
