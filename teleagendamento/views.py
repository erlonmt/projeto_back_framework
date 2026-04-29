from datetime import date

from django.contrib import messages
from django.db.models import Prefetch
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import ConsultaForm
from .models import Consulta, Especialidade, HorarioDisponivel


class AgendaContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["especialidades"] = Especialidade.objects.filter(
            ativo=True,
        ).prefetch_related(
            Prefetch(
                "horarios",
                queryset=HorarioDisponivel.objects.filter(ativo=True).order_by("hora"),
                to_attr="horarios_ativos",
            )
        )
        return context


class ConsultaListView(AgendaContextMixin, ListView):
    model = Consulta
    context_object_name = "consultas"
    template_name = "teleagendamento/consulta_list.html"

    def get_queryset(self):
        return Consulta.objects.select_related("especialidade").order_by(
            "data",
            "hora",
            "paciente",
        )


class ConsultaCreateView(AgendaContextMixin, CreateView):
    model = Consulta
    form_class = ConsultaForm
    template_name = "teleagendamento/consulta_form.html"
    success_url = reverse_lazy("teleagendamento:consulta_list")

    def form_valid(self, form):
        consulta_existente = form.paciente_com_agendamento()
        response = super().form_valid(form)
        messages.success(self.request, "Consulta agendada com sucesso.")

        if consulta_existente:
            messages.warning(
                self.request,
                (
                    "Atenção: este paciente já tinha uma consulta marcada para "
                    f"{consulta_existente.data_formatada} às "
                    f"{consulta_existente.hora_formatada}."
                ),
            )
        return response


class ConsultaUpdateView(AgendaContextMixin, UpdateView):
    model = Consulta
    form_class = ConsultaForm
    template_name = "teleagendamento/consulta_form.html"
    success_url = reverse_lazy("teleagendamento:consulta_list")

    def get_queryset(self):
        return Consulta.objects.select_related("especialidade")

    def form_valid(self, form):
        consulta_existente = form.paciente_com_agendamento()
        response = super().form_valid(form)
        messages.success(self.request, "Consulta atualizada com sucesso.")

        if consulta_existente:
            messages.warning(
                self.request,
                (
                    "Atenção: este paciente também possui consulta marcada para "
                    f"{consulta_existente.data_formatada} às "
                    f"{consulta_existente.hora_formatada}."
                ),
            )
        return response


class HorariosDisponiveisView(View):
    def get(self, request, *args, **kwargs):
        especialidade_id = request.GET.get("especialidade")
        if not especialidade_id:
            return JsonResponse({"horarios": []})

        try:
            especialidade_id = int(especialidade_id)
        except (TypeError, ValueError):
            return JsonResponse({"horarios": []})

        horarios = HorarioDisponivel.objects.filter(
            especialidade_id=especialidade_id,
            especialidade__ativo=True,
            ativo=True,
        ).order_by("hora")

        data_consulta = self.data_consulta()
        if data_consulta:
            hoje = timezone.localdate()
            if data_consulta < hoje:
                return JsonResponse({"horarios": []})

            if data_consulta == hoje:
                horarios = horarios.filter(hora__gt=timezone.localtime().time())

            consultas_ocupadas = Consulta.objects.filter(
                especialidade_id=especialidade_id,
                data=data_consulta,
            )

            consulta_id = self.consulta_id()
            if consulta_id is not None:
                consultas_ocupadas = consultas_ocupadas.exclude(pk=consulta_id)

            horarios = horarios.exclude(
                hora__in=consultas_ocupadas.values_list("hora", flat=True),
            )

        return JsonResponse(
            {
                "horarios": [
                    {
                        "valor": horario.hora.strftime("%H:%M"),
                        "rotulo": horario.hora.strftime("%H:%M"),
                    }
                    for horario in horarios
                ]
            }
        )

    def data_consulta(self):
        data_consulta = self.request.GET.get("data")
        if not data_consulta:
            return None

        try:
            return date.fromisoformat(data_consulta)
        except ValueError:
            return None

    def consulta_id(self):
        consulta_id = self.request.GET.get("consulta")
        if not consulta_id:
            return None

        try:
            return int(consulta_id)
        except (TypeError, ValueError):
            return None


class ConsultaDeleteView(DeleteView):
    model = Consulta
    template_name = "teleagendamento/consulta_confirm_delete.html"
    success_url = reverse_lazy("teleagendamento:consulta_list")

    def form_valid(self, form):
        messages.success(self.request, "Consulta removida com sucesso.")
        return super().form_valid(form)
