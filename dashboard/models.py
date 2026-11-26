from django.conf import settings
from django.db import models


class Activity(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')
    kind = models.CharField(max_length=20, choices=[('visit', 'Visited'), ('search', 'Searched'), ('quiz', 'Quiz'), ('game', 'Game'), ('lesson', 'Lesson'), ('structure', 'Structure'), ('reaction', 'Reaction'), ('experiment', 'Experiment'), ('post', 'Community')], default='visit')
    label = models.CharField(max_length=200)
    url = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.user} {self.kind}: {self.label}'


class ContactMessage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.subject} – {self.email}'

