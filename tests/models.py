from django.db import models

from django_bitmask_field import BitmaskField


class TestModel(models.Model):

    bitmask_choices = BitmaskField(choices=[(1, 0), (2, 1), (4, 2)])
