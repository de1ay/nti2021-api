# Generated by Django 3.1.6 on 2021-02-12 18:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userinfo',
            old_name='name',
            new_name='fio',
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='patronymic',
        ),
        migrations.RemoveField(
            model_name='userinfo',
            name='surname',
        ),
    ]
