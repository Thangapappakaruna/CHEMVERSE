from django.conf import settings
from django.db import models


class Structure(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='structures')
    name = models.CharField(max_length=80)
    formula = models.CharField(max_length=60, blank=True)
    molar_mass = models.FloatField(null=True, blank=True)
    data = models.JSONField(default=dict)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return f'{self.name} ({self.formula})'

