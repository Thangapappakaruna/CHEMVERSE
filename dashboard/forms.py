from django import forms

from config.bootstrap import BootstrapFormMixin

from .models import ContactMessage


class ContactForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ('name', 'email', 'subject', 'message')
        widgets = {'message': forms.Textarea(attrs={'rows': 5})}
