from django.contrib import admin

from .models import Element


@admin.register(Element)
class ElementAdmin(admin.ModelAdmin):
    list_display = ('number', 'symbol', 'name', 'atomic_mass', 'category', 'group', 'period', 'phase')
    list_filter = ('category', 'phase', 'block', 'period')
    search_fields = ('name', 'symbol')
