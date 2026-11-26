from django import forms

from config.bootstrap import BootstrapFormMixin
from config.chem import ChemError

from .logic import parse_side
from .models import Reaction

TYPE_CHOICES = [('auto', 'Detect automatically')] + list(Reaction._meta.get_field('reaction_type').choices)


class ReactionForm(BootstrapFormMixin, forms.Form):
    title = forms.CharField(max_length=120)
    reactants = forms.CharField(max_length=150, help_text='Separate substances with +, coefficients optional. e.g. 2H2 + O2',
                                widget=forms.TextInput(attrs={'class': 'mono', 'placeholder': '2H2 + O2'}))
    products = forms.CharField(max_length=150, help_text='e.g. 2H2O',
                               widget=forms.TextInput(attrs={'class': 'mono', 'placeholder': '2H2O'}))
    reaction_type = forms.ChoiceField(choices=TYPE_CHOICES, initial='auto')
    conditions = forms.CharField(max_length=120, required=False, help_text='e.g. heat, catalyst, aqueous')
    explanation = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3}),
                                  help_text='Describe what happens (optional).')
    is_public = forms.BooleanField(required=False, initial=True, label='Share publicly')

    def _side(self, name):
        try:
            return parse_side(self.cleaned_data[name])
        except ChemError as exc:
            raise forms.ValidationError(str(exc))

    def clean_reactants(self):
        return self._side('reactants')

    def clean_products(self):
        return self._side('products')
