from django.db import models

from django_bitmask_field import BitmaskField


class TestModel(models.Model):

    bitmask = BitmaskField(choices=[(1, 'choice 0'), (4, 'choice 1'), (2147483648, 'choice 2')])


class ContributingModel(models.Model):

    pass
