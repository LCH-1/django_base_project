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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.choices and self.default == models.fields.NOT_PROVIDED:
            self.default = self.choices[0][0]


class ForeignKey(CheckVerboseNameAttributeMixin, CheckRelatedNameAttributeMixin, models.ForeignKey):
    pass


class ManyToManyField(CheckVerboseNameAttributeMixin, CheckRelatedNameAttributeMixin, models.ManyToManyField):
    pass


class OneToOneField(CheckVerboseNameAttributeMixin, models.OneToOneField):
    pass


class FileField(CheckVerboseNameAttributeMixin, models.FileField):
    def __init__(self, *args, **kwargs):
        self.protected = kwargs.pop('protected', False)
        self._upload_to = kwargs.pop('upload_to', None)

        super().__init__(*args, **kwargs)

    def generate_filename(self, instance, filename):
        # app_name = instance._meta.app_label
        model_name = instance._meta.model_name
        field_name = self.name

        ext = filename.split('.')[-1]
        filename = f'{uuid.uuid4().hex}.{ext}'
        fullpath = f"{model_name}/{field_name}/{filename}"

        return f"protected/{fullpath}" if self.protected else fullpath

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        self._check_unsupported_options(cls)
        self._check_protected_valid(cls)

    def _check_unsupported_options(self, model):
        assert not self._upload_to, f"{model.__name__}.{self.name} / upload_to option is not supported"

    def _check_protected_valid(self, model):
        assert isinstance(self.protected, bool), \
            f"{model.__name__}.{self.name} / FileField.protected must be bool, not {type(self.protected)}"

        has_permission_method = hasattr(model, f"has_{self.name}_permission")

        assert (self.protected, has_permission_method) != (True, False), \
            f"{model.__name__}.{self.name} is set to protected=True, model must have has_{self.name}_permission method."

        assert (self.protected, has_permission_method) != (False, True), \
            f"{model.__name__}.{self.name} is set to protected=False, model must not have has_{self.name}_permission method."


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
