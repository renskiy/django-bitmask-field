from django import forms
from django.db import models

from django_bitmask_field import BitmaskField


class TestModel(models.Model):

    bitmask = BitmaskField(
        choices=[(1, 'choice 0'), ('optgroup', [(4, 'choice 1')])],
        null=True
    )
    bitmask_int = BitmaskField(null=True)


class ContributingModel(models.Model):

    pass


class TestForm(forms.ModelForm):

    class Meta:
        model = TestModel
        exclude = ()
