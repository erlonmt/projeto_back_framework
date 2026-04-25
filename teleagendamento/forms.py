from django import forms

from .models import Consulta, Especialidade


class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ["paciente", "especialidade", "data", "hora", "observacoes"]
        widgets = {
            "data": forms.DateInput(attrs={"type": "date"}),
            "hora": forms.TimeInput(attrs={"type": "time", "step": "300"}),
            "observacoes": forms.Textarea(attrs={"rows": 3}),
        }
        labels = {
            "paciente": "Nome completo do paciente",
            "especialidade": "Especialidade",
            "data": "Data da consulta",
            "hora": "Horário",
        }
        help_texts = {
            "hora": "Use um dos horários cadastrados para a especialidade.",
            "observacoes": "Campo opcional para recados internos.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["especialidade"].queryset = Especialidade.objects.filter(
            ativo=True,
        ).order_by("nome", "medico")
        self.fields["especialidade"].empty_label = "Selecione a especialidade"

        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

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
