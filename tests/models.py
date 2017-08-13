from django.db import models

from django_bitmask_field import BitmaskField


class TestModel(models.Model):

    bitmask = BitmaskField(choices=[(1, 'choice 0'), (4, 'choice 1')], null=True)


class ContributingModel(models.Model):

    pass
