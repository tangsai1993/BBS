# Generated by Django 3.2.7 on 2021-12-12 06:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0003_alter_userinfo_is_active'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userinfo',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active'),
        ),
    ]