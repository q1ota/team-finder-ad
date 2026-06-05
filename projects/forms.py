from django import forms

from users.mixins import GitHubUrlMixin

from .models import Project


class ProjectForm(GitHubUrlMixin, forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'description', 'github_url', 'status']
        labels = {
            'name': 'Название проекта',
            'description': 'Описание проекта',
            'github_url': 'Ссылка на GitHub',
            'status': 'Статус',
        }
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'status': forms.Select(),
        }
