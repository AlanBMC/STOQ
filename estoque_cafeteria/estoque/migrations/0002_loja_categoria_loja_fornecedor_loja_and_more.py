# Generated by Django 5.1.4 on 2025-01-04 21:14

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('estoque', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Loja',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
            ],
        ),
        migrations.AddField(
            model_name='categoria',
            name='loja',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='estoque.loja'),
        ),
        migrations.AddField(
            model_name='fornecedor',
            name='loja',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='estoque.loja'),
        ),
        migrations.AddField(
            model_name='movimentoestoque',
            name='loja',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='estoque.loja'),
        ),
        migrations.AddField(
            model_name='produto',
            name='loja',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='estoque.loja'),
        ),
    ]
