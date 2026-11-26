from django.conf import settings
from django.core import signing
from django.core.mail import send_mail
from django.db.models import F
from django.urls import reverse

from .models import Profile

SALT = 'chemverse.email-verification'


def get_profile(user):
    profile, _ = Profile.objects.get_or_create(user=user)
    return profile


def add_xp(user, amount):
    if user.is_authenticated and amount > 0:
        get_profile(user)
        Profile.objects.filter(user=user).update(xp=F('xp') + int(amount))


def make_verification_token(user):
    return signing.dumps({'u': user.pk, 'e': user.email}, salt=SALT)


def read_verification_token(token):
    """Returns (user_id, email) or raises signing.BadSignature / SignatureExpired."""
    data = signing.loads(token, salt=SALT, max_age=settings.EMAIL_VERIFICATION_MAX_AGE)
    return data['u'], data['e']


def send_verification_email(request, user):
    link = request.build_absolute_uri(reverse('accounts:verify_email', args=[make_verification_token(user)]))
    send_mail(
        subject='Verify your CHEMVERSE email',
        message=(f'Hi {user.username},\n\nWelcome to CHEMVERSE! Please confirm your email address by opening this link:\n\n'
                 f'{link}\n\nThe link is valid for 3 days. If you did not create an account, ignore this email.\n\n— CHEMVERSE'),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
