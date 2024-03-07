from datetime import datetime, date

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from rest_framework import fields
from rest_framework import relations
from rest_framework.exceptions import ValidationError

from base_project.utils import ul, yi, wa, en


class DefaultErrorMessageMixin:
    default_error_messages = {
        'required': _("{capital_verbose_name}'s input is required."),
        'null': _("The {verbose_name} is cannot be empty.")
    }

    def bind(self, field_name, parent):
        super().bind(field_name, parent)
        self.verbose_name = f"{self.label[0].lower()}{self.label[1:]}"
        self.capital_verbose_name = force_str(self.label)

        self.custom_format_mapping = {
            "{verbose_name}": f"{self.verbose_name}",
            "{capital_verbose_name}": self.capital_verbose_name,
            "{{을}}": ul(self.verbose_name),
            "{{이}}": yi(self.verbose_name),
            "{{은}}": wa(self.verbose_name),
            "{{과}}": en(self.verbose_name),
        }

    def fail(self, key, **kwargs):
        """
        A helper method that simply raises a validation error.
        """
        try:
            msg = self.error_messages[key]
        except KeyError:
            class_name = self.__class__.__name__
            msg = fields.MISSING_ERROR_MESSAGE.format(class_name=class_name, key=key)
            raise AssertionError(msg)

        for str_, val in self.custom_format_mapping.items():
            if str_ in msg:
                msg = msg.replace(str_, val)

        # if "{verbose_name}" in msg:
        #     kwargs["verbose_name"] = self.verbose_name
        # if "{capital_verbose_name}" in msg:
        #     kwargs["capital_verbose_name"] = self.capital_verbose_name

        message_string = msg.format(**kwargs)

        raise ValidationError(message_string, code=key)


# those are using in rest_framework
class FileField(DefaultErrorMessageMixin, fields.FileField):
    default_error_messages = {
        'required': _('No {verbose_name} file was submitted.'),
        'invalid': _('The submitted {verbose_name} data was not a file. Check the encoding type on the form.'),
        'no_name': _('No {verbose_name} filename could be determined.'),
        'empty': _('The submitted {verbose_name} file is empty.'),
        'max_length': _('Ensure {verbose_name} filename has at most {max_length} characters (it has {length}).'),
    }

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


class CharField(DefaultErrorMessageMixin, fields.CharField):
    default_error_messages = {
        'invalid': _('Not a valid {verbose_name} string.'),
        'blank': _('The {verbose_name} is cannot be empty.'),
        'max_length': _('Ensure {verbose_name} has no more than {max_length} characters.'),
        'min_length': _('Ensure {verbose_name} has at least {min_length} characters.'),
    }


class BooleanField(DefaultErrorMessageMixin, fields.BooleanField):
    default_error_messages = {
        'invalid': _('{capital_verbose_name} must be a valid boolean.')
    }


class DateField(DefaultErrorMessageMixin, fields.DateField):
    default_error_messages = {
        'invalid': _("{capital_verbose_name}'s date has wrong format. Use one of these formats instead: {format}."),
        'datetime': _("{capital_verbose_name}'s xpected a date but got a datetime."),
    }


class DateTimeField(DefaultErrorMessageMixin, fields.DateTimeField):
    default_error_messages = {
        'invalid': _('{capital_verbose_name} has wrong format. Use one of these formats instead: {format}.'),
        'date': _('Expected a {verbose_name} datetime but got a date.'),
        'make_aware': _('Invalid {verbose_name} datetime for the timezone "{timezone}".'),
        'overflow': _('{capital_verbose_name} datetime value out of range.')
    }


class TimeField(DefaultErrorMessageMixin, fields.TimeField):
    default_error_messages = {
        'invalid': _('{capital_verbose_name} time has wrong format. Use one of these formats instead: {format}.'),
    }


class DurationField(DefaultErrorMessageMixin, fields.DurationField):
    default_error_messages = {
        'invalid': _('{capital_verbose_name} duration has wrong format. Use one of these formats instead: {format}.'),
        'max_value': _('Ensure {verbose_name} value is less than or equal to {max_value}.'),
        'min_value': _('Ensure {verbose_name} value is greater than or equal to {min_value}.'),
    }


class EmailField(DefaultErrorMessageMixin, fields.EmailField):
    default_error_messages = {
        'invalid': _('Enter a valid {verbose_name} email address.')
    }


class IntegerField(DefaultErrorMessageMixin, fields.IntegerField):
    default_error_messages = {
        'invalid': _('A valid {verbose_name} integer is required.'),
        'max_value': _('Ensure {verbose_name} value is less than or equal to {max_value}.'),
        'min_value': _('Ensure {verbose_name} value is greater than or equal to {min_value}.'),
        'max_string_length': _('{capital_verbose_name} string value too large.')
    }


class FloatField(DefaultErrorMessageMixin, fields.FloatField):
    default_error_messages = {
        'invalid': _('A valid {verbose_name} number is required.'),
        'max_value': _('Ensure {verbose_name} this value is less than or equal to {max_value}.'),
        'min_value': _('Ensure {verbose_name} this value is greater than or equal to {min_value}.'),
        'max_string_length': _('{capital_verbose_name} string value too large.')
    }


class URLField(DefaultErrorMessageMixin, fields.URLField):
    default_error_messages = {
        'invalid': _('Enter a valid {verbose_name} URL.')
    }


class PrimaryKeyRelatedField(DefaultErrorMessageMixin, relations.PrimaryKeyRelatedField):
    default_error_messages = {
        'required': _("{capital_verbose_name}'s input is required."),
        'does_not_exist': _('Invalid {verbose_name} pk "{pk_value}" - object does not exist.'),
        'incorrect_type': _('Incorrect {verbose_name} type. Expected pk value, received {data_type}.'),
    }


class ChoiceField(DefaultErrorMessageMixin, fields.ChoiceField):
    default_error_messages = {
        'invalid_choice': _('"{input}" is not a valid choice. in {verbose_name}')
    }
