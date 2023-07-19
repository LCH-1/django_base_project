from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from user.models import User


class UserCreationForm(forms.ModelForm):
    '''사용자 생성 폼'''

    email = forms.CharField(
        label='이메일',
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': '이메일',
                'required': 'True',
            }
        )
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Password',
                'required': 'True',
            }
        )
    )
    password2 = forms.CharField(
        label='Password confirmation',
        widget=forms.PasswordInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Password confirmation',
                'required': 'True',
            }
        )
    )

    class Meta:
        model = User
        fields = ('email', )

    def clean_password2(self):
        # 두 비밀번호 입력 일치 확인
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_admin = self.cleaned_data['is_admin']
        user.set_password(self.cleaned_data["password1"])

        if commit:
            user.save()

        return user


class UserChangeForm(forms.ModelForm):
    '''비밀번호 변경 폼'''

    password = ReadOnlyPasswordHashField(
        label='Password',
        help_text=("Raw passwords are not stored, so there is no way to see \
                    this user's password, but you can change the password \
                    using <a href=\"../password/\">this form</a>.")
    )

    class Meta:
        model = User
        fields = ('email', 'password', 'is_active', )

    def clean_password(self):
        return self.initial["password"]
