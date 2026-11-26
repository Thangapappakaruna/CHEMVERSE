from django.conf import settings
from django.db import models


class SavedComparison(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comparisons')
    name = models.CharField(max_length=80)
    compounds = models.ManyToManyField('compound_search.Compound', related_name='comparisons')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

