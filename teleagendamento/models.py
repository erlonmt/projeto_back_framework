from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Especialidade(models.Model):
    nome = models.CharField(max_length=80)
    medico = models.CharField("médico(a)", max_length=100)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nome", "medico"]
        verbose_name = "especialidade"
        verbose_name_plural = "especialidades"
        constraints = [
            models.UniqueConstraint(
                fields=["nome", "medico"],
                name="especialidade_unica_medico",
            )
        ]

    def __str__(self) -> str:
        return self.titulo

    @property
    def titulo(self) -> str:
        return f"{self.nome} - {self.medico}"


class HorarioDisponivel(models.Model):
    especialidade = models.ForeignKey(
        Especialidade,
        on_delete=models.CASCADE,
        related_name="horarios",
    )
    hora = models.TimeField()
    ativo = models.BooleanField(default=True)

    class Meta:
        ordering = ["especialidade__nome", "hora"]
        verbose_name = "horário disponível"
        verbose_name_plural = "horários disponíveis"
        constraints = [
            models.UniqueConstraint(
                fields=["especialidade", "hora"],
                name="horario_unico_especialidade",
            )
        ]

    def __str__(self) -> str:
        return f"{self.especialidade} às {self.hora:%H:%M}"


class Consulta(models.Model):
    paciente = models.CharField(max_length=150)
    especialidade = models.ForeignKey(
        Especialidade,
        on_delete=models.PROTECT,
        related_name="consultas",
    )
    data = models.DateField()
    hora = models.TimeField()
    observacoes = models.TextField("observações", blank=True)
    criada_em = models.DateTimeField(auto_now_add=True)
    atualizada_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["data", "hora", "paciente"]
        verbose_name = "consulta"
        verbose_name_plural = "consultas"
        constraints = [
            models.UniqueConstraint(
                fields=["especialidade", "data", "hora"],
                name="consulta_unica_espec_data_hora",
            )
        ]
        indexes = [
            models.Index(fields=["data", "hora"], name="consulta_data_hora_idx"),
            models.Index(fields=["paciente"], name="consulta_paciente_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.paciente} - {self.especialidade} em {self.data_formatada}"

    @property
    def data_formatada(self) -> str:
        return self.data.strftime("%d/%m/%Y")

    @property
    def hora_formatada(self) -> str:
        return self.hora.strftime("%H:%M")

    def resumo(self) -> str:
        return (
            f"{self.paciente}\n"
            f"{self.especialidade}\n"
            f"{self.data_formatada} às {self.hora_formatada}"
        )

    def clean(self) -> None:
        super().clean()

        if self.paciente:
            self.paciente = self.paciente.strip().title()

        if self.data:
            hoje = timezone.localdate()
            if self.data < hoje:
                raise ValidationError(
                    {"data": "Não é possível marcar consulta para uma data passada."}
                )

            horario_passado = (
                self.hora
                and self.data == hoje
                and self.hora <= timezone.localtime().time()
            )
            if horario_passado:
                raise ValidationError(
                    {"hora": "Este horário já passou. Selecione um horário futuro."}
                )

        if self.especialidade_id and self.hora:
            horarios = HorarioDisponivel.objects.filter(
                especialidade=self.especialidade,
                ativo=True,
            )
            if horarios.exists() and not horarios.filter(hora=self.hora).exists():
                raise ValidationError(
                    {
                        "hora": (
                            "Este horário não está disponível para a "
                            "especialidade selecionada."
                        )
                    }
                )

        if self.especialidade_id and self.data and self.hora:
            consultas_no_horario = Consulta.objects.filter(
                especialidade=self.especialidade,
                data=self.data,
                hora=self.hora,
            )
            if self.pk:
                consultas_no_horario = consultas_no_horario.exclude(pk=self.pk)

            if consultas_no_horario.exists():
                raise ValidationError(
                    {
                        "hora": (
                            "Este horário já está ocupado para esta "
                            "especialidade nesta data."
                        )
                    }
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("teleagendamento:consulta_list")
