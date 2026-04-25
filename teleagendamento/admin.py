from django.contrib import admin

from .models import Consulta, Especialidade, HorarioDisponivel


class HorarioDisponivelInline(admin.TabularInline):
    model = HorarioDisponivel
    extra = 1


@admin.register(Especialidade)
class EspecialidadeAdmin(admin.ModelAdmin):
    list_display = ("nome", "medico", "ativo")
    list_filter = ("ativo",)
    search_fields = ("nome", "medico")
    inlines = [HorarioDisponivelInline]


@admin.register(HorarioDisponivel)
class HorarioDisponivelAdmin(admin.ModelAdmin):
    list_display = ("especialidade", "hora", "ativo")
    list_filter = ("ativo", "especialidade")
    search_fields = ("especialidade__nome", "especialidade__medico")


@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ("paciente", "especialidade", "data", "hora")
    list_filter = ("especialidade", "data")
    search_fields = ("paciente", "especialidade__nome", "especialidade__medico")
    date_hierarchy = "data"
