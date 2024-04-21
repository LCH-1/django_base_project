from pyotp import TOTP

from django import forms
from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm


class AdminOtpAuthForm(AuthenticationForm):
    otp = forms.CharField(required=True, widget=forms.TextInput(attrs={"autocomplete": "off"}), label="otp")
    OTP_ERROR_MESSAGES = {
        "token_required": "Please enter your otp code.",
        "otp_not_set": "This account does not have an otp key set up, please contact the administrator.",
        "invalid_token": "Invalid token. Please make sure you have entered it correctly.",
    }

    def _otp_clean(self):
        if settings.DEBUG:
            return
        otp = self.cleaned_data.get("otp")

        if not otp:
            raise forms.ValidationError(
                self.OTP_ERROR_MESSAGES["token_required"],
                code="token_required",
            )

        user = self.get_user()

        if not user.otp_key:
            raise forms.ValidationError(
                self.OTP_ERROR_MESSAGES["otp_not_set"],
                code="otp_not_set",
            )

        if otp != TOTP(user.otp_key).now():
            raise forms.ValidationError(
                self.OTP_ERROR_MESSAGES["invalid_token"],
                code="invalid_token",
            )

    def clean(self):
        username = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        self.user_cache = authenticate(
            self.request, username=username, password=password
        )

        if self.user_cache is None:
            raise self.get_invalid_login_error()
        else:
            self.confirm_login_allowed(self.user_cache)

        self._otp_clean()

        return self.cleaned_data
