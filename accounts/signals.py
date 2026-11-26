import random

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Profile

COLORS = ['#22d3ee', '#a78bfa', '#34d399', '#f472b6', '#fbbf24', '#60a5fa']


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance, defaults={'avatar_color': random.choice(COLORS),
                                                               'email_verified': instance.is_superuser})
