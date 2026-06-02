import io
import random
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.files.base import ContentFile
from django.db import models
from PIL import Image, ImageDraw, ImageFont


AVATAR_COLORS = [
    '#4A90D9', '#7B68EE', '#50C878', '#FF7F7F',
    '#FFB347', '#87CEEB', '#DDA0DD', '#90EE90',
    '#F08080', '#20B2AA', '#9370DB', '#3CB371',
]


def generate_avatar(letter: str) -> ContentFile:
    size = (200, 200)
    color = random.choice(AVATAR_COLORS)
    img = Image.new('RGB', size, color)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', 100)
    except OSError:
        font = ImageFont.load_default(size=100)

    text = letter.upper()
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]
    x = (size[0] - text_w) / 2 - bbox[0]
    y = (size[1] - text_h) / 2 - bbox[1]
    draw.text((x, y), text, fill='white', font=font)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return ContentFile(buf.getvalue())


class UserManager(BaseUserManager):
    def create_user(self, email, name, surname, password=None, **extra):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, surname=surname, **extra)
        user.set_password(password)
        if not user.avatar:
            avatar_data = generate_avatar(name[0] if name else 'U')
            user.avatar.save(f'avatar_{email}.png', avatar_data, save=False)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, surname, password=None, **extra):
        extra.setdefault('is_staff', True)
        extra.setdefault('is_superuser', True)
        return self.create_user(email, name, surname, password, **extra)


class Skill(models.Model):
    name = models.CharField(max_length=124, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=124)
    surname = models.CharField(max_length=124)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    phone = models.CharField(max_length=12, blank=True, null=True)
    github_url = models.URLField(blank=True)
    about = models.TextField(max_length=256, blank=True)
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
