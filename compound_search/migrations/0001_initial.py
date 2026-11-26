from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Compound',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('formula', models.CharField(max_length=60)),
                ('molar_mass', models.FloatField(null=True, blank=True)),
                ('melting_point', models.FloatField(null=True, blank=True, help_text='°C at 1 atm')),
                ('mp_note', models.CharField(max_length=120, blank=True)),
                ('boiling_point', models.FloatField(null=True, blank=True, help_text='°C at 1 atm')),
                ('bp_note', models.CharField(max_length=120, blank=True)),
                ('state', models.CharField(max_length=10, choices=[('solid', 'Solid'), ('liquid', 'Liquid'), ('gas', 'Gas')], default='solid')),
                ('category', models.CharField(max_length=40)),
                ('description', models.TextField(blank=True)),
                ('chemical_properties', models.TextField(blank=True)),
                ('safety', models.TextField(blank=True)),
                ('data_quality', models.CharField(max_length=20, choices=[('reference', 'Reference value'), ('approximate', 'Approximate'), ('user', 'User submitted')], default='reference')),
                ('added_by', models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='compounds')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['name']},
        ),
        migrations.CreateModel(
            name='ChemicalProperty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('compound', models.ForeignKey('compound_search.Compound', on_delete=models.CASCADE, related_name='properties')),
                ('name', models.CharField(max_length=60)),
                ('value', models.CharField(max_length=160)),
                ('note', models.CharField(max_length=160, blank=True)),
            ],
            options={'ordering': ['id']},
        ),
        migrations.CreateModel(
            name='FavoriteCompound',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorite_compounds')),
                ('compound', models.ForeignKey('compound_search.Compound', on_delete=models.CASCADE, related_name='favorited_by')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'unique_together': [('user', 'compound')], 'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='SearchHistory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='compound_searches')),
                ('query', models.CharField(max_length=100)),
                ('results', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
