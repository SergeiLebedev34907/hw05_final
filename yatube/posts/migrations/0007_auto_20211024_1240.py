# Generated by Django 2.2.16 on 2021-10-24 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0006_auto_20211024_1239'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='text',
            field=models.TextField(max_length=400, verbose_name='Комментарий:'),
        ),
    ]