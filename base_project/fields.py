from django.conf import settings

from rest_framework.fields import FileField as BaseFileField


class FileField(BaseFileField):
    def to_representation(self, value):
        try:
            url = value.url
        except (AttributeError, ValueError):
            return None

        if url.startswith("/api/fileserver/protected/"):
            url = url.split("/")
            url[-1] = str(self.parent.instance.pk)
            url = "/".join(url)

            return url

        return url
