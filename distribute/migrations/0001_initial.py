# Generated by Django 2.0 on 2020-11-03 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ToothWash',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('arrive_num', models.IntegerField()),
                ('time', models.DateField()),
            ],
            options={
                'db_table': 'ygj_tooth_wash',
            },
        ),
    ]
