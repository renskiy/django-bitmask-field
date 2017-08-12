import codecs

from django import forms
from django.core import exceptions, validators
from django.db import models
from django.utils.encoding import force_bytes
from django.utils.functional import cached_property
from django.utils.six import integer_types, buffer_types
from django.utils.six.moves import reduce
from django.utils.translation import ugettext_lazy as _

long = integer_types[-1]


def int2bytes(i):
    hex_value = '{0:x}'.format(i)
    # make length of hex_value a multiple of two
    hex_value = '0' * (len(hex_value) % 2) + hex_value
    return codecs.decode(hex_value, 'hex')


def bytes2int(b):
    return long(codecs.encode(b, 'hex'), 16)


class BitmaskFormField(forms.TypedMultipleChoiceField):

    def prepare_value(self, value):
        if isinstance(value, list):
            return value
        return [
            int(bit) * (2 ** place)
            for place, bit in enumerate('{0:b}'.format(value)[::-1])
        ]

    def has_changed(self, initial, data):
        return initial != data

    def _coerce(self, value):
        values = super(BitmaskFormField, self)._coerce(value)
        return reduce(int.__or__, values, 0)


class BitmaskField(models.BinaryField):

    description = _('Bitmask')
    default_validators = [validators.MinValueValidator(0)]

    def __init__(self, *args, **kwargs):
        editable = kwargs.get('editable', True)
        super(BitmaskField, self).__init__(*args, **kwargs)
        self.editable = editable

    def _check_choices(self):
        errors = super(BitmaskField, self)._check_choices()
        if not errors and self.choices:
            pass  # TODO check keys values (must be positive ints less than 2 ** 32)
        return errors

    def deconstruct(self):
        return models.Field.deconstruct(self)

    @cached_property
    def all_choices(self, _value=0):
        for option_key, option_value in self.choices:
            if isinstance(option_value, (list, tuple)):
                _value |= reduce(int.__or__, next(zip(*option_value)), 0)
            else:
                _value |= option_key
        return _value

    def validate(self, value, model_instance):
        # disable standard self.choices validation by resetting its value
        choices, self.choices = self.choices, None
        try:
            super(BitmaskField, self).validate(value, model_instance)
        finally:
            # resume original self.choices value
            self.choices = choices

        if (
            choices
            and value not in self.empty_values
            and value & self.all_choices != value
        ):
            raise exceptions.ValidationError(
                _('Value %(value)r contains disabled bit(s)'),
                code='disabled_bits',
                params={'value': value},
            )

    def value_to_string(self, obj):
        return models.Field.value_to_string(self, obj)

    def to_python(self, value):
        if isinstance(value, buffer_types):
            return bytes2int(force_bytes(value))
        return value

    def get_prep_value(self, value):
        value = super(BitmaskField, self).get_prep_value(value)
        if value is None:
            return value
        return int2bytes(value)

    def from_db_value(self, value, expression, connection, context):
        return self.to_python(value)

    def formfield(self, **kwargs):
        defaults = {
            'form_class': forms.IntegerField,
            'choices_form_class': BitmaskFormField,
        }
        if self.choices:
            defaults['coerce'] = int
        defaults.update(kwargs)
        return super(BitmaskField, self).formfield(**defaults)


# class BitmaskField(models.IntegerField):
#
#     description = _('Bitmask (4 byte)')
#
#     max_value = 2147483647
#
#     def _check_choices(self):
#         if not self.choices:
#             return [checks.Error("Must provide 'choices'.", obj=self)]
#         errors = super(BitmaskField, self)._check_choices()
#         if not errors:
#             pass  # TODO check keys values (must be positive ints less than 2 ** 32)
#         return errors
#
#     @cached_property
#     def all_choices(self, _value=0):
#         for option_key, option_value in self.choices:
#             if isinstance(option_value, (list, tuple)):
#                 _value |= reduce(int.__or__, next(zip(*option_value)), 0)
#             else:
#                 _value |= option_key
#         return _value
#
#     def validate(self, value, model_instance):
#         # disable standard self.choices validation by resetting its value
#         choices, self.choices = self.choices, None
#         try:
#             super(BitmaskField, self).validate(value, model_instance)
#         finally:
#             # resume original self.choices value
#             self.choices = choices
#
#         if value not in self.empty_values and value & self.all_choices != value:
#             raise exceptions.ValidationError(
#                 _('Value %(value)r contains disabled bit(s)'),
#                 code='disabled_bits',
#                 params={'value': value},
#             )
#
#     def get_choices(self, include_blank=None, *args, **kwargs):
#         return super(BitmaskField, self).get_choices(
#             include_blank=False,
#             *args, **kwargs
#         )
#
#     def from_db_value(self, value, expression, connection, context):
#         if value is not None and value < 0:
#             value += self.max_value + 1
#         return value
#
#     def to_python(self, value):
#         if isinstance(value, list):
#             return sum(map(int, value))
#         return super(BitmaskField, self).to_python(value)
#
#     def get_prep_value(self, value):
#         value = super(BitmaskField, self).get_prep_value(value)
#         if value is None:
#             return value
#         return value - self.max_value - 1 if value > self.max_value else value
#
#     def formfield(self, **kwargs):
#         defaults = {'choices_form_class': BitmaskFormField}
#         defaults.update(kwargs)
#         return super(BitmaskField, self).formfield(**defaults)
#
#
# class BigBitmaskField(BitmaskField, models.BigIntegerField):
#
#     description = _('BigBitmask (8 byte)')
#
#     max_value = models.BigIntegerField.MAX_BIGINT
#
#
# class SmallBitmaskField(BitmaskField, models.SmallIntegerField):
#
#     description = _('SmallBitmask (2 byte)')
#
#     max_value = 32767
