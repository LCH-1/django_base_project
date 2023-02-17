from django.core.validators import RegexValidator

PHONE_VALIDATOR = RegexValidator(regex=r'01[0|1|6|7|8|9]\d{3,4}\d{4}$',
                                 message='올바른 핸드폰 번호를 입력해주세요.',
                                 code='invalid')
