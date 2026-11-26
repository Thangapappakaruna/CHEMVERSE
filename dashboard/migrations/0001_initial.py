from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Activity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activities')),
                ('kind', models.CharField(max_length=20, choices=[('visit', 'Visited'), ('search', 'Searched'), ('quiz', 'Quiz'), ('game', 'Game'), ('lesson', 'Lesson'), ('structure', 'Structure'), ('reaction', 'Reaction'), ('experiment', 'Experiment'), ('post', 'Community')], default='visit')),
                ('label', models.CharField(max_length=200)),
                ('url', models.CharField(max_length=300, blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)),
                ('name', models.CharField(max_length=100)),
                ('email', models.EmailField()),
                ('subject', models.CharField(max_length=150)),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
