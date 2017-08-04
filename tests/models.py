from django.db import models

from django_bitmask_field import (
    BitmaskField, BigBitmaskField, SmallBitmaskField
)


class TestModel(models.Model):

    bitmask = BitmaskField(choices=[(1, 'choice 0'), (4, 'choice 1'), (2147483648, 'choice 2')])
    bitmask_small = SmallBitmaskField(choices=[(1, 'choice 0'), (4, 'choice 1'), (9223372036854775808, 'choice 2')], null=True)
    bitmask_big = BigBitmaskField(choices=[(1, 'choice 0'), (4, 'choice 1'), (32768, 'choice 2')], null=True)


class ContributingModel(models.Model):

    pass
