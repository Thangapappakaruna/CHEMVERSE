"""Adds Bootstrap 5 classes to every form widget."""
from django import forms


class BootstrapFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            w = field.widget
            if isinstance(w, (forms.CheckboxInput,)):
                css = 'form-check-input'
            elif isinstance(w, (forms.CheckboxSelectMultiple, forms.RadioSelect)):
                css = ''
            elif isinstance(w, (forms.Select, forms.SelectMultiple)):
                css = 'form-select'
            else:
                css = 'form-control'
            if css:
                w.attrs['class'] = (w.attrs.get('class', '') + ' ' + css).strip()
