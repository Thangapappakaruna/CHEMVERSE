from django.conf import settings
from django.db import models


class WeightCalculation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='weight_calculations')
    formula = models.CharField(max_length=60)
    molar_mass = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

