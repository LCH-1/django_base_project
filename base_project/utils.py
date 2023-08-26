import re
import os
import uuid
from datetime import datetime

from django.utils.deconstruct import deconstructible


@deconstructible
class FilenameObfusecate:
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        filename = f'{datetime.now().strftime("%Y%m%d%H%M%S%f")}_{uuid.uuid4().hex}.{ext}'

        return os.path.join(self.path, filename)


def ends_with_jong(kstr):
    kstr = kstr.split(" ")[-1]
    m = re.search("[가-힣]+", str(kstr))

    if m:
        k = m.group()[-1]
        return (ord(k) - ord("가")) % 28 > 0

    return ""


def ul(kstr):
    end = "을" if ends_with_jong(kstr) else "를"
    return f'{kstr}{end}'


def yi(kstr):
    end = "이" if ends_with_jong(kstr) else "가"
    return f'{kstr}{end}'


def wa(kstr):
    end = "과" if ends_with_jong(kstr) else "와"
    return f'{kstr}{end}'


def en(kstr):
    end = "은" if ends_with_jong(kstr) else "는"
    return f'{kstr}{end}'


def get_select_related_fields(model):
    meta = model._meta

    # fk, one to one 정참조
    direct_choices = [f.name for f in meta.fields if f.is_relation]

    # one to one 역참조
    reverse_choices = [f.field.related_query_name() for f in meta.related_objects if f.field.unique]

    return direct_choices + reverse_choices


def get_prefetch_related_fields(model):
    meta = model._meta

    # many to many 제외 역참조
    reverse_choices = [x.field.related_query_name() for x in meta.related_objects if not x.many_to_many and not x.one_to_one]

    # many to many
    manytomany_choices = [x.name for x in meta.many_to_many]

    return reverse_choices + manytomany_choices
