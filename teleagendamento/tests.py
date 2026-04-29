from datetime import date, time

from django.core.exceptions import ValidationError
from django.forms import Select
from django.test import TestCase
from django.urls import reverse

from .forms import ConsultaForm
from .models import Consulta, Especialidade, HorarioDisponivel


class ConsultaModelTests(TestCase):
    def setUp(self):
        self.especialidade, _ = Especialidade.objects.get_or_create(
            nome="Cardiologia",
            medico="Dr. João",
        )
        HorarioDisponivel.objects.get_or_create(
            especialidade=self.especialidade,
            hora=time(8, 0),
        )
        HorarioDisponivel.objects.get_or_create(
            especialidade=self.especialidade,
            hora=time(9, 0),
        )

    def test_normaliza_nome_do_paciente_ao_salvar(self):
        consulta = Consulta.objects.create(
            paciente="maria da silva",
            especialidade=self.especialidade,
            data=date(2026, 5, 8),
            hora=time(8, 0),
        )

        self.assertEqual(consulta.paciente, "Maria Da Silva")

    def test_bloqueia_horario_ja_ocupado(self):
        Consulta.objects.create(
            paciente="Maria Silva",
            especialidade=self.especialidade,
            data=date(2026, 5, 8),
            hora=time(8, 0),
        )

        with self.assertRaises(ValidationError):
            Consulta.objects.create(
                paciente="João Santos",
                especialidade=self.especialidade,
                data=date(2026, 5, 8),
                hora=time(8, 0),
            )

    def test_bloqueia_horario_fora_do_catalogo_da_especialidade(self):
        consulta = Consulta(
            paciente="Ana Lima",
            especialidade=self.especialidade,
            data=date(2026, 5, 8),
            hora=time(11, 0),
        )

        with self.assertRaises(ValidationError):
            consulta.full_clean()

    def test_permite_atualizar_consulta_mantendo_o_mesmo_horario(self):
        consulta = Consulta.objects.create(
            paciente="Maria Silva",
            especialidade=self.especialidade,
            data=date(2026, 5, 8),
            hora=time(8, 0),
        )

        consulta.paciente = "Maria Souza"
        consulta.save()

        self.assertEqual(consulta.paciente, "Maria Souza")

    def test_pagina_inicial_carrega_agenda(self):
        resposta = self.client.get(reverse("teleagendamento:consulta_list"))

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Agenda do Complexo Hospitalar UPE")

    def test_formulario_exibe_horarios_da_especialidade_em_select(self):
        formulario = ConsultaForm(initial={"especialidade": self.especialidade.pk})

        self.assertIsInstance(formulario.fields["hora"].widget, Select)
        escolhas = dict(formulario.fields["hora"].choices)
        self.assertEqual(escolhas["08:00"], "08:00")
        self.assertEqual(escolhas["09:00"], "09:00")
        self.assertNotIn("11:00", escolhas)

    def test_formulario_cria_consulta(self):
        resposta = self.client.post(
            reverse("teleagendamento:consulta_create"),
            {
                "paciente": "Pedro Almeida",
                "especialidade": self.especialidade.pk,
                "data": "2026-05-08",
                "hora": "08:00",
                "observacoes": "",
            },
        )

        self.assertRedirects(resposta, reverse("teleagendamento:consulta_list"))
        self.assertTrue(Consulta.objects.filter(paciente="Pedro Almeida").exists())

    def test_horarios_disponiveis_filtra_horario_ocupado_na_data(self):
        Consulta.objects.create(
            paciente="Maria Silva",
            especialidade=self.especialidade,
            data=date(2026, 5, 8),
            hora=time(8, 0),
        )

        resposta = self.client.get(
            reverse("teleagendamento:horarios_disponiveis"),
            {
                "especialidade": self.especialidade.pk,
                "data": "2026-05-08",
            },
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(
            resposta.json()["horarios"],
            [
                {"valor": "09:00", "rotulo": "09:00"},
                {"valor": "10:00", "rotulo": "10:00"},
            ],
        )
