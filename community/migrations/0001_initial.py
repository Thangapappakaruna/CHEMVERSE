from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('reaction_builder', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')),
                ('title', models.CharField(max_length=150)),
                ('body', models.TextField()),
                ('category', models.CharField(max_length=20, choices=[('question', 'Question'), ('discussion', 'Discussion'), ('reaction', 'Shared reaction'), ('resource', 'Resource')], default='discussion')),
                ('shared_reaction', models.ForeignKey('reaction_builder.Reaction', null=True, blank=True, on_delete=models.SET_NULL, related_name='posts')),
                ('likes', models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='liked_posts')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post', models.ForeignKey('community.Post', on_delete=models.CASCADE, related_name='comments')),
                ('author', models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')),
                ('body', models.TextField(max_length=2000)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['created_at']},
        ),
    ]
