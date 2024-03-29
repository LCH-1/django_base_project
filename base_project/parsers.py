from rest_framework.parsers import JSONParser, FormParser, MultiPartParser, DataAndFiles


class RemoveEmptyValueMixin:
    """
    Json, Form parser의 empty value 제거 mixin
    """

    def parse(self, stream, media_type=None, parser_context=None):
        data_ = super().parse(stream, media_type=media_type, parser_context=parser_context)
        data = {k: v for k, v in data_.items() if v != "" and v is not None}

        return data


class RemoveEmptyValueJSONParser(RemoveEmptyValueMixin, JSONParser):
    pass


class RemoveEmptyValueFormParser(RemoveEmptyValueMixin, FormParser):
    pass


class RemoveEmptyValueMultiPartParser(MultiPartParser):
    """
    MultiPartParser의 empty value 제거
    """

    def parse(self, stream, media_type=None, parser_context=None):
        result = super().parse(stream, media_type=media_type, parser_context=parser_context)
        data = result.data.copy()

        for key in [k for k, v in data.items() if v == "" or v is None]:
            del data[key]

        return DataAndFiles(data, result.files)
