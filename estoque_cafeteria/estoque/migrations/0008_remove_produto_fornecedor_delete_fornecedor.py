# Generated by Django 5.1.4 on 2025-02-10 15:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0007_loja_logo'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='produto',
            name='fornecedor',
        ),
        migrations.DeleteModel(
            name='Fornecedor',
        ),
    ]
