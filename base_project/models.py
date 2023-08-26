import uuid

from django.db import models
from django.db.models import SET_NULL, CASCADE
from django.core import checks, validators


class Model(models.Model):
    def __str__(self):
        raise NotImplementedError('`__str__()` must be implemented.')

    class Meta:
        abstract = True
        ordering = ['-pk']


class CheckVerboseNameAttributeMixin:
    def _check_verbose_name_attribute(self, **kwargs):
        if not self._verbose_name:
            return [
                checks.Error(
                    "field must define a 'verbose_name' attribute.",
                    obj=self,
                )
            ]

        return []

    def check(self, **kwargs):
        errors = super().check(**kwargs)
        errors.extend(self._check_verbose_name_attribute(**kwargs))
        return errors


class CheckRelatedNameAttributeMixin:
    def _check_related_name_attribute(self, **kwargs):
        if not self._related_name:
            return [
                checks.Error(
                    "field must define a 'related_name' attribute.",
                    obj=self,
                )
            ]

        return []

    def check(self, **kwargs):
        errors = super().check(**kwargs)
        errors.extend(self._check_related_name_attribute(**kwargs))
        return errors


class CharField(CheckVerboseNameAttributeMixin, models.CharField):
    pass


class ForeignKey(CheckVerboseNameAttributeMixin, CheckRelatedNameAttributeMixin, models.ForeignKey):
    pass


class ManyToManyField(CheckVerboseNameAttributeMixin, CheckRelatedNameAttributeMixin, models.ManyToManyField):
    pass


class OneToOneField(CheckVerboseNameAttributeMixin, models.OneToOneField):
    pass


class FileField(CheckVerboseNameAttributeMixin, models.FileField):
    pass


class TextField(CheckVerboseNameAttributeMixin, models.TextField):
    pass


class BooleanField(CheckVerboseNameAttributeMixin, models.BooleanField):
    pass


class DateField(CheckVerboseNameAttributeMixin, models.DateField):
    pass


class DateTimeField(CheckVerboseNameAttributeMixin, models.DateTimeField):
    pass


class DurationField(CheckVerboseNameAttributeMixin, models.DurationField):
    pass


class EmailField(CheckVerboseNameAttributeMixin, models.EmailField):
    pass


class IntegerField(CheckVerboseNameAttributeMixin, models.IntegerField):
    pass


class GenericIPAddressField(CheckVerboseNameAttributeMixin, models.GenericIPAddressField):
    pass


class PositiveIntegerField(CheckVerboseNameAttributeMixin, models.PositiveIntegerField):
    pass


class TimeField(CheckVerboseNameAttributeMixin, models.TimeField):
    pass


class URLField(CheckVerboseNameAttributeMixin, models.URLField):
    pass
