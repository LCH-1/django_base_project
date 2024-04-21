from django.db.models import FileField as BaseFileField

from rest_framework import serializers
from rest_framework.serializers import BaseSerializer
from rest_framework.exceptions import ErrorDetail, ValidationError

from base_project import models
from base_project.fields import (
    FileField, CharField, BooleanField, DateField, DateTimeField,
    TimeField, DurationField, EmailField, IntegerField, FloatField,
    PrimaryKeyRelatedField, ChoiceField, URLField,
)


class ResponseErrorSerializerMixin:
    """
    error response 시 list가 아닌 string 형태로 반환
    """

    def is_valid(self, *, raise_exception=False, keep_origin=False):
        if keep_origin:
            return super().is_valid(raise_exception=raise_exception)

        assert hasattr(self, 'initial_data'), (
            'Cannot call `.is_valid()` as no `data=` keyword argument was '
            'passed when instantiating the serializer instance.'
        )

        if not hasattr(self, '_validated_data'):
            try:
                self._validated_data = self.run_validation(self.initial_data)
            except ValidationError as exc:
                self._validated_data = {}
                self._errors = exc.detail
            else:
                self._errors = {}

        if self._errors:
            first_error = next(iter(self._errors.items()))[1]
            first_error = first_error[0]

            self._errors = {
                "error": first_error
            }

            if raise_exception:
                raise ValidationError(self.errors)

        return not bool(self._errors)


class Serializer(ResponseErrorSerializerMixin, serializers.Serializer):
    pass


class ModelSerializer(ResponseErrorSerializerMixin, serializers.ModelSerializer):
    """
    default error message 및 커스텀 옵션들을 적용하기 위해 serializer field mapping 재정의
    """
    serializer_field_mapping = serializers.ModelSerializer.serializer_field_mapping
    serializer_field_mapping[models.BooleanField] = BooleanField
    serializer_field_mapping[models.CharField] = CharField
    serializer_field_mapping[models.DateField] = DateField
    serializer_field_mapping[models.DurationField] = DurationField
    serializer_field_mapping[models.DateTimeField] = DateTimeField
    serializer_field_mapping[models.EmailField] = EmailField
    serializer_field_mapping[models.FileField] = FileField
    serializer_field_mapping[models.FloatField] = FloatField
    serializer_field_mapping[models.IntegerField] = IntegerField
    serializer_field_mapping[models.PositiveIntegerField] = IntegerField
    serializer_field_mapping[models.TextField] = CharField
    serializer_field_mapping[models.TimeField] = TimeField
    serializer_field_mapping[models.URLField] = URLField

    serializer_related_field = PrimaryKeyRelatedField
    serializer_choice_field = ChoiceField


class ListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        pass


class RawListSerializer(ListSerializer):
    @property
    def data(self):
        return super(serializers.ListSerializer, self).data


class WritableSerializerMethodField(serializers.SerializerMethodField):
    def __init__(self, method_name=None, **kwargs):
        super().__init__(method_name, **kwargs)
        self.read_only = False

    def to_internal_value(self, data):
        model = self.parent.Meta.model
        field = getattr(model, self.field_name).field

        if isinstance(field, (models.ForeignKey, models.OneToOneField)):
            fk_model = field.remote_field.model
            try:
                data = fk_model.objects.get(pk=data)
            except fk_model.DoesNotExist as e:
                raise ValidationError(f"올바르지 않은 {field.verbose_name} 입니다.") from e

        elif isinstance(field, (models.ManyToManyField)):
            fk_model = field.remote_field.model
            queryset = fk_model.objects.filter(pk__in=data)
            if len(data) != queryset.count():
                raise ValidationError(f"올바르지 않은 {field.verbose_name} 입니다.")

            data = queryset

        return {self.field_name: data}


class PrimaryKeyRelatedWriteField(serializers.PrimaryKeyRelatedField):
    def __new__(cls, *args, **kwargs):
        kwargs['write_only'] = True

        return super().__new__(cls, *args, **kwargs)

    def __init__(self, model, **kwargs):
        filter_query = kwargs.pop('filter_query', {})
        kwargs['queryset'] = model.objects.filter(**filter_query)

        super().__init__(**kwargs)
