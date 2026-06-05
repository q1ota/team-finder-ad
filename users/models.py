from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .constants import ABOUT_MAX_LENGTH, NAME_MAX_LENGTH, PHONE_MAX_LENGTH, SKILL_NAME_MAX_LENGTH
from .managers import UserManager
from .service import generate_avatar


class Skill(models.Model):
    name = models.CharField(max_length=SKILL_NAME_MAX_LENGTH, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=NAME_MAX_LENGTH)
    surname = models.CharField(max_length=NAME_MAX_LENGTH)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    phone = models.CharField(max_length=PHONE_MAX_LENGTH, blank=True, null=True)
    github_url = models.URLField(blank=True)
    about = models.TextField(max_length=ABOUT_MAX_LENGTH, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    skills = models.ManyToManyField(Skill, blank=True, related_name='users')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'surname']

    objects = UserManager()

    def save(self, *args, **kwargs):
        if not self.pk and not self.avatar:
            letter = self.name[0] if self.name else 'U'
            avatar_data = generate_avatar(letter)
            self.avatar.save(f'avatar_{self.email}.png', avatar_data, save=False)
        super().save(*args, **kwargs)

    def get_full_name(self):
        return f'{self.name} {self.surname}'

    def __str__(self):
        return self.email
