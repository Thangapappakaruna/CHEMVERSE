from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [

    ]

    operations = [
        migrations.CreateModel(
            name='Term',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('term', models.CharField(max_length=80, unique=True)),
                ('slug', models.SlugField(max_length=90, unique=True)),
                ('definition', models.TextField()),
                ('category', models.CharField(max_length=40)),
                ('example', models.CharField(max_length=250, blank=True)),
            ],
            options={'ordering': ['term']},
        ),
    ]
