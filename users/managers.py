from django.contrib.auth.models import BaseUserManager

from .service import generate_avatar


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
