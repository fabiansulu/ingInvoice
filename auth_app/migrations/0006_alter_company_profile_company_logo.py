# Generated by Django 5.0.1 on 2024-02-07 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_app', '0005_company_profile_company_logo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='company_profile',
            name='company_logo',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
