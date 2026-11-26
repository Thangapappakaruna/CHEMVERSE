from django.contrib import admin

from .models import Term


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    list_display = ('term', 'category')
    list_filter = ('category',)
    search_fields = ('term', 'definition')
    prepopulated_fields = {'slug': ('term',)}
