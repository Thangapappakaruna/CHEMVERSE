from django import forms

from config.bootstrap import BootstrapFormMixin
from config.chem import ChemError, molar_mass

from .models import Compound


class CompoundForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Compound
        fields = ('name', 'formula', 'melting_point', 'mp_note', 'boiling_point', 'bp_note', 'state', 'category',
                  'description', 'chemical_properties', 'safety')
        labels = {'melting_point': 'Melting point (°C)', 'boiling_point': 'Boiling point (°C)',
                  'mp_note': 'Melting point note', 'bp_note': 'Boiling point note'}
        help_texts = {'mp_note': 'e.g. “decomposes”, “sublimes”, “approximate”', 'formula': 'e.g. C2H5OH or Ca(OH)2'}
        widgets = {f: forms.Textarea(attrs={'rows': 2}) for f in ('description', 'chemical_properties', 'safety')}

    def clean_formula(self):
        f = self.cleaned_data['formula'].strip()
        try:
            self._mm = molar_mass(f)
        except ChemError as exc:
            raise forms.ValidationError(str(exc))
        return f

    def clean(self):
        data = super().clean()
        mp, bp = data.get('melting_point'), data.get('boiling_point')
        if mp is not None and bp is not None and bp < mp:
            raise forms.ValidationError('The boiling point cannot be lower than the melting point.')
        for f in ('melting_point', 'boiling_point'):
            v = data.get(f)
            if v is not None and v < -273.15:
                self.add_error(f, 'Below absolute zero (−273.15 °C) is impossible.')
        return data

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.molar_mass = getattr(self, '_mm', None)
        obj.data_quality = 'user'
        if commit:
            obj.save()
        return obj
