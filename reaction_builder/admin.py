from django.contrib import admin

from .models import Reaction


@admin.register(Reaction)
class ReactionAdmin(admin.ModelAdmin):
    list_display = ('title', 'equation', 'reaction_type', 'is_balanced', 'is_sample', 'user', 'created_at')
    list_filter = ('reaction_type', 'is_balanced', 'is_sample', 'is_public')
    search_fields = ('title', 'equation')
