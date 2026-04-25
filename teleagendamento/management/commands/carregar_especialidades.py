from datetime import time

from django.core.management.base import BaseCommand

from teleagendamento.data import ESPECIALIDADES_PADRAO
from teleagendamento.models import Especialidade, HorarioDisponivel


def criar_hora(valor: str) -> time:
    hora, minuto = [int(parte) for parte in valor.split(":")]
    return time(hour=hora, minute=minuto)


class Command(BaseCommand):
    help = "Carrega as especialidades e horários padrão do teleagendamento."

    def handle(self, *args, **options):
        especialidades_criadas = 0
        horarios_criados = 0

        for item in ESPECIALIDADES_PADRAO:
            especialidade, criada = Especialidade.objects.get_or_create(
                nome=item["nome"],
                medico=item["medico"],
                defaults={"ativo": True},
            )
            if criada:
                especialidades_criadas += 1

            for horario in item["horarios"]:
                _, horario_criado = HorarioDisponivel.objects.get_or_create(
                    especialidade=especialidade,
                    hora=criar_hora(horario),
                    defaults={"ativo": True},
                )
                if horario_criado:
                    horarios_criados += 1

        self.stdout.write(
            self.style.SUCCESS(
                "Carga concluída: "
                f"{especialidades_criadas} especialidade(s) e "
                f"{horarios_criados} horário(s) criado(s)."
            )
        )
