from django.conf import settings
from django.db import models


class Compound(models.Model):
    name = models.CharField(max_length=100)
    formula = models.CharField(max_length=60)
    molar_mass = models.FloatField(null=True, blank=True)
    melting_point = models.FloatField(null=True, blank=True, help_text='°C at 1 atm')
    mp_note = models.CharField(max_length=120, blank=True)
    boiling_point = models.FloatField(null=True, blank=True, help_text='°C at 1 atm')
    bp_note = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=10, choices=[('solid', 'Solid'), ('liquid', 'Liquid'), ('gas', 'Gas')], default='solid')
    category = models.CharField(max_length=40)
    description = models.TextField(blank=True)
    chemical_properties = models.TextField(blank=True)
    safety = models.TextField(blank=True)
    data_quality = models.CharField(max_length=20, choices=[('reference', 'Reference value'), ('approximate', 'Approximate'), ('user', 'User submitted')], default='reference')
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='compounds')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.formula})'

    def state_at(self, t):
        if self.melting_point is not None and t < self.melting_point:
            return 'solid'
        if self.boiling_point is not None and t >= self.boiling_point:
            return 'gas'
        if self.melting_point is None and self.boiling_point is not None and t < self.boiling_point:
            return 'solid'
        return 'liquid'


class ChemicalProperty(models.Model):
    compound = models.ForeignKey('compound_search.Compound', on_delete=models.CASCADE, related_name='properties')
    name = models.CharField(max_length=60)
    value = models.CharField(max_length=160)
    note = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f'{self.compound.name}: {self.name}'


class FavoriteCompound(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorite_compounds')
    compound = models.ForeignKey('compound_search.Compound', on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('user', 'compound')]
        ordering = ['-created_at']


class SearchHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='compound_searches')
    query = models.CharField(max_length=100)
    results = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

