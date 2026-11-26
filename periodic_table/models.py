from django.db import models

CATEGORY_LABELS = {
    'alkali-metal': 'Alkali metal', 'alkaline-earth': 'Alkaline earth metal', 'transition': 'Transition metal',
    'post-transition': 'Post-transition metal', 'metalloid': 'Metalloid', 'nonmetal': 'Reactive non-metal',
    'halogen': 'Halogen', 'noble-gas': 'Noble gas', 'lanthanide': 'Lanthanide', 'actinide': 'Actinide',
}


class Element(models.Model):
    number = models.PositiveSmallIntegerField(unique=True)
    symbol = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=40)
    atomic_mass = models.FloatField()
    mass_is_estimate = models.BooleanField(default=False, help_text='Mass number of the most stable isotope')
    category = models.CharField(max_length=20)
    period = models.PositiveSmallIntegerField()
    group = models.PositiveSmallIntegerField(null=True, blank=True)
    block = models.CharField(max_length=1)
    phase = models.CharField(max_length=10)
    melting_point = models.FloatField(null=True, blank=True, help_text='°C at 1 atm')
    boiling_point = models.FloatField(null=True, blank=True, help_text='°C at 1 atm')

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f'{self.number} {self.symbol} {self.name}'

    @property
    def category_label(self):
        return CATEGORY_LABELS.get(self.category, self.category)

    @property
    def mass_display(self):
        return f'[{int(self.atomic_mass)}]' if self.mass_is_estimate else f'{self.atomic_mass:g}'

    @property
    def grid_col(self):
        if 57 <= self.number <= 71:
            return self.number - 54
        if 89 <= self.number <= 103:
            return self.number - 86
        return self.group

    @property
    def grid_row(self):
        if 57 <= self.number <= 71:
            return 9
        if 89 <= self.number <= 103:
            return 10
        return self.period

    def to_dict(self):
        return {f: getattr(self, f) for f in ('number', 'symbol', 'name', 'atomic_mass', 'mass_is_estimate', 'category',
                                              'period', 'group', 'block', 'phase', 'melting_point', 'boiling_point')}

