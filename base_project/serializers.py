from django.db import models

from rest_framework import serializers
from rest_framework.serializers import BaseSerializer, Serializer
from rest_framework.exceptions import ErrorDetail, ValidationError
from rest_framework.fields import (
    BooleanField, CharField, ChoiceField, DateField, DateTimeField, EmailField,
    IntegerField, SerializerMethodField, TimeField, IPAddressField
)

from base_project.fields import FileField
from base_project.utils import ul


class ModelSerializer(serializers.ModelSerializer):
    serializer_field_mapping = serializers.ModelSerializer.serializer_field_mapping
    serializer_field_mapping[models.FileField] = FileField

    def set_default_error_messages(self, extra_kwargs):
        meta = getattr(self, 'Meta')
        model = meta.model
        fields = self.fields

        for field_name in fields:
            field_dict = extra_kwargs.get(field_name)

            try:
                field = getattr(model, field_name).field
            except AttributeError:
                continue

            verbose_name = field.verbose_name
            # TODO settings.LANGUAGE_CODE에 따라 다른 언어로 에러 메세지 출력
            if isinstance(field, models.FileField):
                message = '업로드'
                # message = 'upload'

            else:
                message = '입력'
                # message = 'enter'

            default_error_messages = {
                'blank': f'{ul(verbose_name)} {message}해주세요.',
                'required': f'{ul(verbose_name)} {message}해주세요.',
                'invalid': f'알맞은 형식의 {ul(verbose_name)} {message}해주세요.',
            }

            # default_error_messages = {
            #     'blank': f'please {message} {verbose_name}',
            #     'required': f'please {message} {verbose_name}',
            #     'invalid': f'please {message} {verbose_name} in the valid format',
            # }

            if field_dict:
                field_dict.setdefault('error_messages', {})
                field_dict['error_messages'] = default_error_messages | field_dict['error_messages']

            else:
                extra_kwargs[field_name] = {'error_messages': default_error_messages}

        return extra_kwargs

    def get_extra_kwargs(self):
        extra_kwargs = super().get_extra_kwargs()
        extra_kwargs = self.set_default_error_messages(extra_kwargs)

        return extra_kwargs

    def get_field_names(self, declared_fields, info):
        self.fields = super().get_field_names(declared_fields, info)

        return self.fields

    # TODO : nested model create 시 테스트 필요
    def is_valid(self, *, raise_exception=False):
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
                # "error": first_error[0] if isinstance(first_error, list) else first_error
            }

            # self._errors = {key: [ErrorDetail(message) for message in value] for key, value in self._errors.items()[0]}

            if raise_exception:
                raise ValidationError(self.errors)

        return not bool(self._errors)


class ListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        pass


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
