from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Lesson',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True)),
                ('title', models.CharField(max_length=120)),
                ('category', models.CharField(max_length=40)),
                ('level', models.CharField(max_length=20, choices=[('Beginner', 'Beginner'), ('Intermediate', 'Intermediate'), ('Advanced', 'Advanced')], default='Beginner')),
                ('order', models.PositiveSmallIntegerField(default=0)),
                ('summary', models.CharField(max_length=250)),
                ('content', models.TextField()),
                ('reading_minutes', models.PositiveSmallIntegerField(default=5)),
            ],
            options={'ordering': ['order']},
        ),
        migrations.CreateModel(
            name='LessonProgress',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lesson_progress')),
                ('lesson', models.ForeignKey('chemistry_learning.Lesson', on_delete=models.CASCADE, related_name='progress')),
                ('completed_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'unique_together': [('user', 'lesson')], 'ordering': ['-completed_at']},
        ),
    ]
