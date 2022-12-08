# Generated by Django 4.0.8 on 2022-12-07 15:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0003_alter_dailyincome_date_alter_weeklyincome_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dailyincome',
            name='date',
            field=models.DateField(auto_now_add=True, unique=True, verbose_name='date'),
        ),
        migrations.AlterField(
            model_name='weeklyincome',
            name='date',
            field=models.DateField(auto_now_add=True, unique=True, verbose_name='date'),
        ),
    ]
