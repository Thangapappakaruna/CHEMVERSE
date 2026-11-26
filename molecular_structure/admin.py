from django.contrib import admin

from .models import Structure


@admin.register(Structure)
class StructureAdmin(admin.ModelAdmin):
    list_display = ('name', 'formula', 'molar_mass', 'user', 'is_public', 'updated_at')
    list_filter = ('is_public',)
    search_fields = ('name', 'formula', 'user__username')
