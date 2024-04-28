from django.core.validators import RegexValidator

PHONE_VALIDATOR = RegexValidator(regex=r'01[0|1|6|7|8|9]\d{3,4}\d{4}$',
                                 message='올바른 핸드폰 번호를 입력해주세요.',
                                 code='invalid')

USERNAME_VALIDATOR = RegexValidator(regex=r'^[a-zA-Z0-9_]{4,20}$',
                                    message='영문, 숫자, _로만 이루어진 4~20자리의 아이디를 입력해주세요.',
                                    code='invalid')
