from django import forms
from django.core import exceptions, checks
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from six import integer_types
from six.moves import reduce

long = integer_types[-1]  # long(codecs.encode(b'hello', 'hex'), 16)


class BitmaskFormField(forms.TypedMultipleChoiceField):

    def prepare_value(self, value):
        if not isinstance(value, list):
            return [
                int(bit) * (2 ** place)
                for place, bit in enumerate('{:b}'.format(value)[::-1])
            ]
        return value

    def has_changed(self, initial, data):
        return forms.Field.has_changed(self, initial, data)

    def _coerce(self, value):
        if value == self.empty_value or value in self.empty_values:
            return self.empty_value
        return self.coerce(value)


# TODO use BinaryField
class BitmaskField(models.IntegerField):

    description = _('Bitmask (4 byte)')

    max_value = 2147483647

    def _check_choices(self):
        if not self.choices:
            return [checks.Error("Must provide 'choices'.", obj=self)]
        errors = super(BitmaskField, self)._check_choices()
        if not errors:
            pass  # TODO check keys values (must be positive ints less than 2 ** 32)
        return errors

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

        if value not in self.empty_values and value & self.all_choices != value:
            raise exceptions.ValidationError(
                _('Value %(value)r contains disabled bit(s)'),
                code='disabled_bits',
                params={'value': value},
            )

    def get_choices(self, include_blank=None, *args, **kwargs):
        return super(BitmaskField, self).get_choices(
            include_blank=False,
            *args, **kwargs
        )

    def from_db_value(self, value, expression, connection, context):
        if value is not None and value < 0:
            value += self.max_value + 1
        return value

    def to_python(self, value):
        if isinstance(value, list):
            return sum(map(int, value))
        return super(BitmaskField, self).to_python(value)

    def get_prep_value(self, value):
        value = super(BitmaskField, self).get_prep_value(value)
        if value is None:
            return value
        return value - self.max_value - 1 if value > self.max_value else value

    def formfield(self, **kwargs):
        defaults = {'choices_form_class': BitmaskFormField}
        defaults.update(kwargs)
        return super(BitmaskField, self).formfield(**defaults)


class BigBitmaskField(BitmaskField, models.BigIntegerField):

    description = _('BigBitmask (8 byte)')

    max_value = models.BigIntegerField.MAX_BIGINT


class SmallBitmaskField(BitmaskField, models.SmallIntegerField):

    description = _('SmallBitmask (2 byte)')

    max_value = 32767
