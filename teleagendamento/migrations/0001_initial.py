from datetime import time

import django.db.models.deletion
from django.db import migrations, models


ESPECIALIDADES_PADRAO = [
    ("Cardiologia", "Dr. João", ["08:00", "09:00", "10:00"]),
    ("Pediatria", "Dra. Maria", ["13:00", "14:00", "15:00"]),
    ("Ortopedia", "Dr. Lucas", ["09:30", "10:30", "11:30"]),
    ("Dermatologia", "Dra. Ana", ["08:30", "09:30", "10:30"]),
    ("Ginecologia", "Dra. Paula", ["14:00", "15:00", "16:00"]),
    ("Clínico Geral", "Dr. Roberto", ["07:00", "08:00", "09:00"]),
]


def criar_hora(valor):
    hora, minuto = [int(parte) for parte in valor.split(":")]
    return time(hour=hora, minute=minuto)


def carregar_especialidades(apps, schema_editor):
    Especialidade = apps.get_model("teleagendamento", "Especialidade")
    HorarioDisponivel = apps.get_model("teleagendamento", "HorarioDisponivel")

    for nome, medico, horarios in ESPECIALIDADES_PADRAO:
        especialidade, _ = Especialidade.objects.get_or_create(
            nome=nome,
            medico=medico,
            defaults={"ativo": True},
        )
        for horario in horarios:
            HorarioDisponivel.objects.get_or_create(
                especialidade=especialidade,
                hora=criar_hora(horario),
                defaults={"ativo": True},
            )


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Especialidade",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nome", models.CharField(max_length=80)),
                ("medico", models.CharField(max_length=100, verbose_name="médico(a)")),
                ("ativo", models.BooleanField(default=True)),
                ("criado_em", models.DateTimeField(auto_now_add=True)),
                ("atualizado_em", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "especialidade",
                "verbose_name_plural": "especialidades",
                "ordering": ["nome", "medico"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("nome", "medico"),
                        name="especialidade_unica_medico",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="HorarioDisponivel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("hora", models.TimeField()),
                ("ativo", models.BooleanField(default=True)),
                (
                    "especialidade",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="horarios",
                        to="teleagendamento.especialidade",
                    ),
                ),
            ],
            options={
                "verbose_name": "horário disponível",
                "verbose_name_plural": "horários disponíveis",
                "ordering": ["especialidade__nome", "hora"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("especialidade", "hora"),
                        name="horario_unico_especialidade",
                    )
                ],
            },
        ),
        migrations.CreateModel(
            name="Consulta",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("paciente", models.CharField(max_length=150)),
                ("data", models.DateField()),
                ("hora", models.TimeField()),
                ("observacoes", models.TextField(blank=True, verbose_name="observações")),
                ("criada_em", models.DateTimeField(auto_now_add=True)),
                ("atualizada_em", models.DateTimeField(auto_now=True)),
                (
                    "especialidade",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="consultas",
                        to="teleagendamento.especialidade",
                    ),
                ),
            ],
            options={
                "verbose_name": "consulta",
                "verbose_name_plural": "consultas",
                "ordering": ["data", "hora", "paciente"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("especialidade", "data", "hora"),
                        name="consulta_unica_espec_data_hora",
                    )
                ],
                "indexes": [
                    models.Index(fields=["data", "hora"], name="consulta_data_hora_idx"),
                    models.Index(fields=["paciente"], name="consulta_paciente_idx"),
                ],
            },
        ),
        migrations.RunPython(carregar_especialidades, migrations.RunPython.noop),
    ]
