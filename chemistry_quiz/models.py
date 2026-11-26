from django.conf import settings
from django.db import models


class Question(models.Model):
    text = models.CharField(max_length=300)
    option_a = models.CharField(max_length=150)
    option_b = models.CharField(max_length=150)
    option_c = models.CharField(max_length=150)
    option_d = models.CharField(max_length=150)
    answer = models.CharField(max_length=1, choices=[('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D')])
    category = models.CharField(max_length=40)
    difficulty = models.CharField(max_length=10, choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], default='easy')
    explanation = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return self.text

    @property
    def options(self):
        return [('a', self.option_a), ('b', self.option_b), ('c', self.option_c), ('d', self.option_d)]


class QuizResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_results')
    category = models.CharField(max_length=40, blank=True)
    difficulty = models.CharField(max_length=10, blank=True)
    score = models.PositiveSmallIntegerField()
    total = models.PositiveSmallIntegerField()
    percent = models.PositiveSmallIntegerField()
    duration_seconds = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

