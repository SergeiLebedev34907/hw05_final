# Generated by Django 2.2.16 on 2021-10-24 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0004_comment"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="comment",
            options={
                "ordering": ["-created"],
                "verbose_name": "Комментарий",
                "verbose_name_plural": "Комментарии",
            },
        ),
        migrations.AlterField(
            model_name="comment",
            name="created",
            field=models.DateTimeField(
                auto_now_add=True, verbose_name="Дата комментария"
            ),
        ),
    ]
