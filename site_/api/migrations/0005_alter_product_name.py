# Generated by Django 3.2.8 on 2022-02-05 02:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_category_eng_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=200),
        ),
    ]
