from rest_framework import serializers


class WritableSerializerMethodField(serializers.SerializerMethodField):
    def __init__(self, method_name=None, **kwargs):
        super().__init__(method_name, **kwargs)
        self.read_only = False

    def to_internal_value(self, data):
        return {self.field_name: data}


class PrimaryKeyRelatedWriteField(serializers.PrimaryKeyRelatedField):
    def __new__(cls, *args, **kwargs):
        kwargs['write_only'] = True

        return super().__new__(cls, *args, **kwargs)

    def __init__(self, model, **kwargs):
        filter_query = kwargs.pop('filter_query', {})
        kwargs['queryset'] = model.objects.filter(**filter_query)

        super().__init__(**kwargs)
