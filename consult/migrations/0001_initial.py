# Generated by Django 2.0 on 2020-11-03 17:49

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Active',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.IntegerField()),
                ('active', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'ygj_active',
            },
        ),
        migrations.CreateModel(
            name='InfoWork',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('channel', models.IntegerField()),
                ('order', models.IntegerField()),
                ('arrive', models.IntegerField()),
                ('title', models.IntegerField()),
                ('sale', models.IntegerField()),
                ('time', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'ygj_info_work',
            },
        ),
        migrations.CreateModel(
            name='SwtWork',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('swt_form_or_zz', models.IntegerField()),
                ('swt_active_form_or_jz', models.IntegerField()),
                ('swt_phone_or_tm', models.IntegerField()),
                ('swt_active_phone_or_xxm', models.IntegerField()),
                ('swt_xm', models.IntegerField()),
                ('sale', models.IntegerField()),
                ('time', models.DateField(blank=True, null=True)),
            ],
            options={
                'db_table': 'ygj_swt_work',
            },
        ),
    ]
