from django.conf import settings
from django.db import models


class Experiment(models.Model):
    slug = models.SlugField(unique=True)
    title = models.CharField(max_length=100)
    summary = models.CharField(max_length=250)
    category = models.CharField(max_length=40)
    safety_note = models.CharField(max_length=250, blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


class ExperimentLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='experiment_logs')
    experiment = models.ForeignKey('lab_simulator.Experiment', on_delete=models.CASCADE, related_name='logs')
    result = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

