from django.conf import settings
from django.db import models


class Game(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=80)
    description = models.CharField(max_length=250)
    icon = models.CharField(max_length=30, default='gamepad')
    max_points = models.PositiveIntegerField(default=5000)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class GameScore(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='game_scores')
    game = models.ForeignKey('chemistry_games.Game', on_delete=models.CASCADE, related_name='scores')
    points = models.PositiveIntegerField()
    details = models.CharField(max_length=120, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

