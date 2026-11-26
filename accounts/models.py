from django.conf import settings
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=100, blank=True)
    bio = models.CharField(max_length=250, blank=True)
    institution = models.CharField(max_length=120, blank=True)
    avatar_color = models.CharField(max_length=7, default='#22d3ee')
    email_verified = models.BooleanField(default=False)
    xp = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Profile of {self.user}'

    @property
    def display_name(self):
        return self.full_name or self.user.username

    @property
    def level(self):
        return self.xp // 150 + 1

    @property
    def level_progress(self):
        return round(100 * (self.xp % 150) / 150)

