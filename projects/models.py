from django.conf import settings
from django.db import models
from django.urls import reverse

from .constants import NAME_MAX_LENGTH, STATUS_CLOSED, STATUS_MAX_LENGTH, STATUS_OPEN


class Project(models.Model):
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_CLOSED, 'Closed'),
    ]

    name = models.CharField(max_length=NAME_MAX_LENGTH)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects',
    )
    created_at = models.DateTimeField(auto_now_add=True)
    github_url = models.URLField(blank=True)
    status = models.CharField(max_length=STATUS_MAX_LENGTH, choices=STATUS_CHOICES, default=STATUS_OPEN)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name='participated_projects',
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('projects:project_detail', kwargs={'pk': self.pk})
