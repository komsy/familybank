# Generated by Django 4.1.5 on 2023-03-07 09:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('expenses', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterModelOptions(
            name='expense',
            options={'ordering': ['-date']},
        ),
    ]
