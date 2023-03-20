from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser

from base_project.validators import PHONE_VALIDATOR
from base_project.utils import FilenameObfusecate


class UserManager(BaseUserManager):
    def create_user(self, password=None, **kwargs):
        user = self.model(**kwargs)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, **kwargs):
        user = self.create_user(**kwargs)
        user.is_admin = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser):
    email = models.EmailField("이메일", unique=True)
    fullname = models.CharField("이름", max_length=50)

    is_active = models.BooleanField("계정 활성화 여부", default=True)
    is_admin = models.BooleanField("admin 여부", default=False)
    join_date = models.DateField("가입일", auto_now_add=True)
    phone = models.CharField("핸드폰 번호", validators=[PHONE_VALIDATOR], unique=True, max_length=20)
    profile_image = models.FileField("프로필 사진", upload_to=FilenameObfusecate("account/user/profile_image"), null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, perm, obj=None):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    def __str__(self) -> str:
        return f"{self.email} / {self.join_date}"
