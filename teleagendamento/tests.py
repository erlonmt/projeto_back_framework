from datetime import date, time

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

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
