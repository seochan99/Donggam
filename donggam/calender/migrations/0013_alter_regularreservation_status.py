# Generated by Django 4.1.4 on 2023-01-21 13:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("calender", "0012_alter_regularreservation_created_at"),
    ]

    operations = [
        migrations.AlterField(
            model_name="regularreservation",
            name="status",
            field=models.CharField(
                choices=[("1", "검토중"), ("2", "승인완료"), ("3", "재확인 필요")], max_length=1
            ),
        ),
    ]
