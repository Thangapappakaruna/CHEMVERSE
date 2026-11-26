from django.contrib import admin

from .models import Question, QuizResult


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'category', 'difficulty', 'answer')
    list_filter = ('category', 'difficulty')
    search_fields = ('text',)


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'difficulty', 'score', 'total', 'percent', 'created_at')
    list_filter = ('difficulty',)
