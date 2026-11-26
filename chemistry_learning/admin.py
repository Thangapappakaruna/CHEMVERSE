from django.contrib import admin

from .models import Lesson, LessonProgress


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('order', 'title', 'category', 'level')
    list_filter = ('category', 'level')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'summary')


admin.site.register(LessonProgress)
