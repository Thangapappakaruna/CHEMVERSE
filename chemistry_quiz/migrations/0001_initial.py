from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=300)),
                ('option_a', models.CharField(max_length=150)),
                ('option_b', models.CharField(max_length=150)),
                ('option_c', models.CharField(max_length=150)),
                ('option_d', models.CharField(max_length=150)),
                ('answer', models.CharField(max_length=1, choices=[('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D')])),
                ('category', models.CharField(max_length=40)),
                ('difficulty', models.CharField(max_length=10, choices=[('easy', 'Easy'), ('medium', 'Medium'), ('hard', 'Hard')], default='easy')),
                ('explanation', models.CharField(max_length=300, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='QuizResult',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_results')),
                ('category', models.CharField(max_length=40, blank=True)),
                ('difficulty', models.CharField(max_length=10, blank=True)),
                ('score', models.PositiveSmallIntegerField()),
                ('total', models.PositiveSmallIntegerField()),
                ('percent', models.PositiveSmallIntegerField()),
                ('duration_seconds', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
