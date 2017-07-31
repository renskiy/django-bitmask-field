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

    description = _('bitmask')

    def validate(self, value, model_instance):
        if self.choices and value not in self.empty_values:
            max_option_key = 0
            for option_key, option_value in self.choices:
                if isinstance(option_value, (list, tuple)):
                    max_option_key = max(
                        max_option_key,
                        max(*tuple(zip(*option_value))[0]),
                    )
                else:
                    max_option_key = max(max_option_key, option_key)
            if value > max_option_key * 2 - 1:
                raise exceptions.ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': value},
                )
            # values containing several enabled bits do not equal to any
            # option_key, so we set it to max_option_key to pass next validation
            value = max_option_key
        super(BitmaskField, self).validate(value, model_instance)

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
