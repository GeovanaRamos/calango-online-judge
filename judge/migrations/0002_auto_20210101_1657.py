# Generated by Django 3.1.4 on 2021-01-01 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('judge', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='result',
            field=models.CharField(blank=True, choices=[('ACCEPTED', 'Aceito'), ('WRONG_ANSWER', 'Resposta Incorreta'), ('PRESENTATION_ERROR', 'Erro de Apresentação'), ('COMPILATION_ERROR', 'Erro de Compilação'), ('RUNTIME_ERROR', 'Erro de Execução'), ('TIME_LIMIT_EXCEEDED', 'Limite de Tempo Excedido'), ('WAITING', 'Aguardando')], editable=False, max_length=30, null=True, verbose_name='Resultado'),
        ),
    ]
