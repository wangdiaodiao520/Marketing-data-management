# Generated by Django 2.0 on 2020-11-03 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DoctorType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('doctor_type', models.CharField(max_length=50)),
            ],
            options={
                'db_table': 'ygj_doctor_type',
            },
        ),
    ]
