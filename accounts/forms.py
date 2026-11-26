from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.validators import RegexValidator

from config.bootstrap import BootstrapFormMixin

from .models import Profile

User = get_user_model()
user_id_validator = RegexValidator(r'^[A-Za-z0-9_.]{3,30}$', 'Use 3–30 letters, numbers, dots or underscores.')


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    username = forms.CharField(label='User ID', max_length=30, validators=[user_id_validator],
                               help_text='Your unique public ID, e.g. curie_fan.')
    email = forms.EmailField(label='Email address')
    full_name = forms.CharField(label='Full name', max_length=100, required=False)

    field_order = ['username', 'email', 'full_name', 'password1', 'password2']

    class Meta:
        model = User
        fields = ('username', 'email')

    def clean_username(self):
        u = self.cleaned_data['username']
        if User.objects.filter(username__iexact=u).exists():
            raise forms.ValidationError('This User ID is already taken.')
        return u

    def clean_email(self):
        e = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=e).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return e

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Profile.objects.filter(user=user).update(full_name=self.cleaned_data.get('full_name', ''))
        return user


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    username = forms.CharField(label='User ID or email', max_length=254,
                               widget=forms.TextInput(attrs={'autofocus': True, 'autocomplete': 'username'}))
    remember_me = forms.BooleanField(required=False, initial=True, label='Keep me signed in')

    error_messages = {
        'invalid_login': 'Incorrect User ID/email or password.',
        'inactive': 'This account is inactive.',
    }


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('full_name', 'institution', 'bio', 'avatar_color')
        widgets = {'avatar_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control-color'}), 'bio': forms.Textarea(attrs={'rows': 3})}


class AccountEmailForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ('email',)

    def clean_email(self):
        e = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=e).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Another account already uses this email.')
        return e
