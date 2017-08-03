from django import forms
from django.core import exceptions
from django.db import models
from django.utils.translation import ugettext_lazy as _


class BitmaskFormField(forms.TypedMultipleChoiceField):

    def prepare_value(self, value):
        if not isinstance(value, list):
            return [
                int(bit) * 2 ** place
                for place, bit in enumerate('{:b}'.format(value)[::-1])
            ]
        return value

    def has_changed(self, initial, data):
        return forms.Field.has_changed(self, initial, data)

    def _coerce(self, value):
        if value == self.empty_value or value in self.empty_values:
            return self.empty_value
        return self.coerce(value)


class BitmaskField(models.IntegerField):

    # TODO if value > 127: value = -(value ^ 128) - 1,
    # reverse: if value < 0: abs(value + 1) ^ 128

    description = _('Bitmask')

    def _check_choices(self):
        errors = super(BitmaskField, self)._check_choices()
        if not errors:
            pass  # TODO check keys values (must be positive ints less than 2 ** 32)
        return errors

    def validate(self, value, model_instance):
        # disable standard self.choices validation by resetting its value
        choices, self.choices = self.choices, None
        try:
            super(BitmaskField, self).validate(value, model_instance)
        finally:
            # resume original self.choices value
            self.choices = choices

        if choices and value not in self.empty_values:
            for option_key, option_value in choices:
                if isinstance(option_value, (list, tuple)):
                    for optgroup_key, optgroup_value in option_value:
                        value ^= optgroup_key
                else:
                    value ^= option_key
            if value:
                raise exceptions.ValidationError(
                    _('Value s(value)r contains disabled bit(s)'),
                    code='disabled_bits',
                    params={'value': value},
                )

    def get_choices(self, include_blank=None, *args, **kwargs):
        return super(BitmaskField, self).get_choices(
            include_blank=False,
            *args, **kwargs
        )

    def to_python(self, value):
        if isinstance(value, list):
            return sum(map(int, value))
        return super(BitmaskField, self).to_python(value)

    def formfield(self, **kwargs):
        defaults = {'choices_form_class': BitmaskFormField}
        defaults.update(kwargs)
        return super(BitmaskField, self).formfield(**defaults)
