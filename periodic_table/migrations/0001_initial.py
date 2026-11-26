from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [

    ]

    operations = [
        migrations.CreateModel(
            name='Element',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.PositiveSmallIntegerField(unique=True)),
                ('symbol', models.CharField(max_length=3, unique=True)),
                ('name', models.CharField(max_length=40)),
                ('atomic_mass', models.FloatField()),
                ('mass_is_estimate', models.BooleanField(default=False, help_text='Mass number of the most stable isotope')),
                ('category', models.CharField(max_length=20)),
                ('period', models.PositiveSmallIntegerField()),
                ('group', models.PositiveSmallIntegerField(null=True, blank=True)),
                ('block', models.CharField(max_length=1)),
                ('phase', models.CharField(max_length=10)),
                ('melting_point', models.FloatField(null=True, blank=True, help_text='°C at 1 atm')),
                ('boiling_point', models.FloatField(null=True, blank=True, help_text='°C at 1 atm')),
            ],
            options={'ordering': ['number']},
        ),
    ]
