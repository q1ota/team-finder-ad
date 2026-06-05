from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import PasswordChangeForm

from .constants import NAME_MAX_LENGTH
from .mixins import GitHubUrlMixin
from .models import User
from .service import normalize_phone


class RegisterForm(forms.Form):
    name = forms.CharField(max_length=NAME_MAX_LENGTH, label='Имя')
    surname = forms.CharField(max_length=NAME_MAX_LENGTH, label='Фамилия')
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует.')
        return email


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')

    def clean(self):
        cleaned = super().clean()
        email = cleaned.get('email')
        password = cleaned.get('password')
        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                raise forms.ValidationError('Неверный имейл или пароль')
            cleaned['user'] = user
        return cleaned


class EditProfileForm(GitHubUrlMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'surname', 'avatar', 'about', 'phone', 'github_url']
        labels = {
            'name': 'Имя',
            'surname': 'Фамилия',
            'avatar': 'Аватар',
            'about': 'О себе',
            'phone': 'Телефон',
            'github_url': 'GitHub',
        }
        widgets = {
            'about': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            return None
        normalized = normalize_phone(phone)
        if normalized is None:
            raise forms.ValidationError(
                'Введите номер в формате 8XXXXXXXXXX или +7XXXXXXXXXX.'
            )
        qs = User.objects.filter(phone=normalized)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Этот номер телефона уже занят.')
        return normalized


class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label='Старый пароль', widget=forms.PasswordInput)
    new_password1 = forms.CharField(label='Новый пароль', widget=forms.PasswordInput)
    new_password2 = forms.CharField(label='Подтверждение пароля', widget=forms.PasswordInput)
