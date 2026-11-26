from django.contrib import admin

from .models import Activity, ContactMessage


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'kind', 'label', 'created_at')
    list_filter = ('kind',)
    search_fields = ('user__username', 'label')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'name', 'email', 'created_at')
    search_fields = ('subject', 'email', 'message')
