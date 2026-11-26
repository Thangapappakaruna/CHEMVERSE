from django.contrib import admin

from .models import Game, GameScore


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'slug', 'max_points')


@admin.register(GameScore)
class GameScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'points', 'created_at')
    list_filter = ('game',)
