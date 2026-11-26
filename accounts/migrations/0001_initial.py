from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')),
                ('full_name', models.CharField(max_length=100, blank=True)),
                ('bio', models.CharField(max_length=250, blank=True)),
                ('institution', models.CharField(max_length=120, blank=True)),
                ('avatar_color', models.CharField(max_length=7, default='#22d3ee')),
                ('email_verified', models.BooleanField(default=False)),
                ('xp', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
