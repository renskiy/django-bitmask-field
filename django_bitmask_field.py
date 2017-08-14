import codecs
import functools

from django import forms
from django.core import checks, exceptions, validators
from django.db import models
from django.utils.encoding import force_bytes
from django.utils.six import integer_types, buffer_types, text_type
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
        if not value:
            return value
        return [
            long(bit) * (2 ** place)
            for place, bit in enumerate('{0:b}'.format(value)[::-1])
            if bit == '1'
        ]

    def has_changed(self, initial, data):
        return initial != self._coerce(data)

    def _coerce(self, value):
        values = super(BitmaskFormField, self)._coerce(value)
        if values is None:
            return values
        return reduce(long.__or__, map(long, values), long(0))


class BitmaskField(models.BinaryField):

    description = _('Bitmask')
    default_validators = [validators.MinValueValidator(0)]

    def __init__(self, *args, **kwargs):
        editable = kwargs.get('editable', True)
        super(BitmaskField, self).__init__(*args, **kwargs)
        self.editable = editable
        self.validators = list(self.__validators)

    @property
    def __validators(self):
        for validator in self.validators:
            if isinstance(validator, validators.MaxLengthValidator):
                max_value = 2 ** (validator.limit_value * 8)
                yield validators.MaxValueValidator(max_value)
            else:
                yield validator

    def _check_choices(self):
        errors = super(BitmaskField, self)._check_choices()
        if not errors and self.choices and not all(
            isinstance(choice, integer_types) and choice >= 0
            for choice, description in self.flatchoices
        ):
            return [
                checks.Error(
                    "all 'choices' must be of integer type.",
                    obj=self,
                )
            ]
        return errors

    def deconstruct(self):
        return models.Field.deconstruct(self)

    @property
    def all_values(self):
        return reduce(
            long.__or__,
            map(long, list(zip(*self.flatchoices))[0]),
            long(0),
        )

    def validate(self, value, model_instance):
        try:
            super(BitmaskField, self).validate(value, model_instance)
        except exceptions.ValidationError as error:
            if error.code != 'invalid_choice':
                raise

        if (
            self.choices
            and value not in self.empty_values
            and value & self.all_values != value
        ):
            raise exceptions.ValidationError(
                self.error_messages['invalid_choice'],
                code='invalid_choice',
                params={'value': value},
            )

    def value_to_string(self, obj):
        return models.Field.value_to_string(self, obj)

    def to_python(self, value):
        if isinstance(value, buffer_types):
            return bytes2int(force_bytes(value))
        elif isinstance(value, text_type):
            return long(value)
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
            'form_class': functools.partial(forms.IntegerField, min_value=0),
            'choices_form_class': BitmaskFormField,
        }
        if self.choices:
            defaults['coerce'] = long
        defaults.update(kwargs)
        return super(BitmaskField, self).formfield(**defaults)
