from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Reaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name='reactions')),
                ('title', models.CharField(max_length=120)),
                ('reactants', models.JSONField(default=list)),
                ('products', models.JSONField(default=list)),
                ('equation', models.CharField(max_length=300)),
                ('reaction_type', models.CharField(max_length=20, choices=[('synthesis', 'Synthesis'), ('decomposition', 'Decomposition'), ('single', 'Single displacement'), ('double', 'Double displacement'), ('combustion', 'Combustion'), ('neutralisation', 'Neutralisation'), ('redox', 'Redox'), ('other', 'Other')], default='other')),
                ('conditions', models.CharField(max_length=120, blank=True)),
                ('explanation', models.TextField(blank=True)),
                ('is_balanced', models.BooleanField(default=False)),
                ('is_public', models.BooleanField(default=True)),
                ('is_sample', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
