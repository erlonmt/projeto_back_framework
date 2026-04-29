from django import forms
from django.utils.dateparse import parse_time

from .models import Consulta, Especialidade, HorarioDisponivel


class ConsultaForm(forms.ModelForm):
    hora = forms.ChoiceField(
        label="Horário",
        help_text="Selecione um horário disponível para o médico escolhido.",
        widget=forms.Select,
        error_messages={
            "invalid_choice": "Selecione um horário cadastrado para este médico.",
            "required": "Selecione o horário da consulta.",
        },
    )

    class Meta:
        model = Consulta
        fields = ["paciente", "especialidade", "data", "hora", "observacoes"]
        widgets = {
            "data": forms.DateInput(attrs={"type": "date"}),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "paciente": "Nome completo do paciente",
            "especialidade": "Especialidade",
            "data": "Data da consulta",
        }
        help_texts = {
            "observacoes": "Campo opcional para recados internos.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["especialidade"].queryset = Especialidade.objects.filter(
            ativo=True,
        ).order_by("nome", "medico")
        self.fields["especialidade"].empty_label = "Selecione a especialidade"
        self.fields["hora"].choices = self.horarios_da_especialidade()

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    def especialidade_selecionada_id(self) -> int | None:
        if self.is_bound:
            valor = self.data.get(self.add_prefix("especialidade"))
        elif self.initial.get("especialidade"):
            valor = self.initial["especialidade"]
        else:
            valor = self.instance.especialidade_id

        try:
            return int(valor)
        except (TypeError, ValueError):
            return None

    def horarios_da_especialidade(self) -> list[tuple[str, str]]:
        especialidade_id = self.especialidade_selecionada_id()
        if not especialidade_id:
            return [("", "Selecione a especialidade primeiro")]

        horarios = HorarioDisponivel.objects.filter(
            especialidade_id=especialidade_id,
            ativo=True,
        ).order_by("hora")
        escolhas = [
            (horario.hora.strftime("%H:%M"), horario.hora.strftime("%H:%M"))
            for horario in horarios
        ]

        if (
            self.instance.pk
            and self.instance.especialidade_id == especialidade_id
            and self.instance.hora
        ):
            hora_atual = self.instance.hora.strftime("%H:%M")
            if hora_atual not in {valor for valor, _ in escolhas}:
                escolhas.append((hora_atual, hora_atual))
                escolhas.sort()

        if escolhas:
            return [("", "Selecione um horário")] + escolhas

        return [("", "Nenhum horário cadastrado para este médico")]

    def clean_hora(self):
        hora = parse_time(self.cleaned_data["hora"])
        if hora is None:
            raise forms.ValidationError("Selecione um horário válido.")
        return hora

    def clean_paciente(self) -> str:
        paciente = self.cleaned_data["paciente"].strip().title()
        if len(paciente) < 3:
            raise forms.ValidationError("Informe um nome de paciente válido.")
        return paciente

    def paciente_com_agendamento(self) -> Consulta | None:
        paciente = self.cleaned_data.get("paciente")
        if not paciente:
            return None

        consultas = Consulta.objects.filter(paciente__iexact=paciente).order_by(
            "data",
            "hora",
        )
        if self.instance.pk:
            consultas = consultas.exclude(pk=self.instance.pk)
        return consultas.first()
