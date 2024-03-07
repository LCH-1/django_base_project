import uuid

from django.db import models, IntegrityError
from django.db.models import SET_NULL, CASCADE, UniqueConstraint, Manager
from django.db.models.fields.files import FieldFile as BaseFieldFile
from django.core import checks, validators
from django.core.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist as DoesNotExist
from django.template.defaultfilters import filesizeformat


class Model(models.Model):
    def __str__(self):
        raise NotImplementedError('`__str__()` must be implemented.')

    class Meta:
        abstract = True
        ordering = ['-pk']


class SingletonManager(models.Manager):
    def get(self, *args, **kwargs):
        try:
            return super().get()
        except DoesNotExist:
            return None


class SingletonModel(Model):
    objects = SingletonManager()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        # 저장한 데이터를 덮어씌우는 경우
        self.pk = 1

        # 에러를 발생시키는 경우
        # if not self.pk and self.__class__.objects.exists():
        # raise IntegrityError("SiteSettings 모델에 이미 데이터가 존재합니다.")

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        IntegrityError('SingletonModel cannot be deleted.')


class CheckVerboseNameAttributeMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
    count = int  # resolve pylint-django's no member error
    all = list  # resolve pylint-django's no member error


class OneToOneField(CheckVerboseNameAttributeMixin, models.OneToOneField):
    pass


class FieldFile(BaseFieldFile):
    def _get_path(self, base_path):
        if not self.field.protected:
            return base_path

        return f"{'/'.join(base_path.split('/')[:-1])}/{self.instance.pk}"

    @property
    def url(self):
        return self._get_path(super().url)

    # def __str__(self):
    #     return self._get_path(self.name)


class FileField(CheckVerboseNameAttributeMixin, models.FileField):
    """
    Same as FileField, but you can specify:
        * allowed_content_types - list containing allowed content_types. Example: ['pdf', 'png', 'jpg', 'jpeg']
        * max_upload_size - a number indicating the maximum file size allowed for upload.
            Examples
             - 1024 # 1kb
             - 10 * 1024 # 10kb
             - 10 * 1024 * 1024 # 10mb
             - 1kb
             - 10mb
             - 1g or 10g
    """
    attr_class = FieldFile

    def __init__(self, *args, **kwargs):
        self.obfuscated = kwargs.pop('obfuscated', True)
        self.protected = kwargs.pop('protected', False)
        self._upload_to = kwargs.pop('upload_to', None)
        self.allowed_content_types = kwargs.pop("allowed_content_types", [])
        self.max_upload_size = kwargs.pop("max_upload_size", 0)

        super().__init__(*args, **kwargs)

        self.validators.append(self._validate_allowed_content_types)
        self.validators.append(self._validate_max_upload_size)

    def _validate_allowed_content_types(self, data):
        # data.content_type : image/png
        # data.name : image.png
        try:
            content_type = data.content_type.split("/")[1]  # TODO 확장자 가져오는거 체크
        except:
            content_type = data.name.rsplit(".")[-1]

        if self.allowed_content_types and content_type not in self.allowed_content_types:
            raise ValidationError('Filetype not supported.')

    def _validate_max_upload_size(self, data):
        if self.max_upload_size > 0 and data.size > self.max_upload_size:
            raise ValidationError(f'Please keep filesize under {filesizeformat(self.max_upload_size)}. Current filesize {filesizeformat(data.size)}')

    def generate_filename(self, instance, filename):
        # app_name = instance._meta.app_label
        model_name = instance._meta.model_name
        field_name = self.name

        if self.obfuscated:
            if "." in filename:
                ext = filename.split('.')[-1]
                filename = f'{uuid.uuid4().hex}.{ext}'
            else:
                filename = f'{uuid.uuid4().hex}'

        fullpath = f"{model_name}/{field_name}/{filename}"

        return f"protected/{fullpath}" if self.protected else fullpath

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)
        self._check_unsupported_options(cls)
        self._check_protected_valid(cls)
        self._check_max_upload_size(cls)

    def _check_max_upload_size(self, model):
        units = {
            "kb": 1024,
            "mb": 1024 * 1024,
            "gb": 1024 * 1024 * 1024,
            "g": 1024 * 1024 * 1024,
        }

        if isinstance(self.max_upload_size, int):
            return

        # assert isinstance(self.max_upload_size, str), f"{model.__name__}.{self.name} / max_upload_size must be int or str, not {type(self.max_upload_size)}"

        for unit, value in units.items():
            if not self.max_upload_size.lower().endswith(unit):
                continue

            try:
                self.max_upload_size = int(self.max_upload_size.replace(unit, "")) * value
                return
            except ValueError:
                break

        raise ValueError(f"{model.__name__}.{self.name} is not valid max_upload_size. It must be int or str like '3kb', '5mb', '2gb' or '2g'")

    def _check_unsupported_options(self, model):
        assert not self._upload_to, f"{model.__name__}.{self.name} / upload_to option is not supported"

    def _check_protected_valid(self, model):
        assert isinstance(self.protected, bool), \
            f"{model.__name__}.{self.name} / FileField.protected must be bool, not {type(self.protected)}"

        # TODO check permission is async
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
    strftime = str  # resolve pylint-django's no member error


class TimeField(CheckVerboseNameAttributeMixin, models.TimeField):
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


class FloatField(CheckVerboseNameAttributeMixin, models.FloatField):
    pass


class URLField(CheckVerboseNameAttributeMixin, models.URLField):
    pass
