from django.contrib import messages
from django.db.models import Prefetch
from django.urls import reverse_lazy
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


class ConsultaDeleteView(DeleteView):
    model = Consulta
    template_name = "teleagendamento/consulta_confirm_delete.html"
    success_url = reverse_lazy("teleagendamento:consulta_list")

    def form_valid(self, form):
        messages.success(self.request, "Consulta removida com sucesso.")
        return super().form_valid(form)
