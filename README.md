# Complexo Hospitalar UPE - Sistema de Teleagendamento

Sistema web desenvolvido com Django para gerenciar o teleagendamento de consultas do Complexo Hospitalar UPE.

O projeto nasceu a partir de uma aplicação Python de terminal e foi migrado para uma versão web com persistência em banco de dados, painel administrativo, interface responsiva e regras de validação para evitar conflitos de agenda.

## Visão Geral

A aplicação permite cadastrar, listar, alterar e cancelar consultas médicas. Cada especialidade possui horários previamente cadastrados, e o sistema impede que duas consultas sejam marcadas para a mesma especialidade, data e horário.

Também existe um alerta quando um paciente já possui outro agendamento, ajudando a equipe a evitar duplicidades.

## Funcionalidades

- Cadastro de novas consultas.
- Listagem completa da agenda.
- Alteração e remarcação de consultas.
- Cancelamento de consultas.
- Validação de horários disponíveis por especialidade.
- Bloqueio de conflito para especialidade, data e horário já ocupados.
- Alerta para paciente com consulta já existente.
- Cadastro e edição de especialidades pelo Django Admin.
- Cadastro e edição de horários disponíveis pelo Django Admin.
- Interface web responsiva baseada na identidade visual da UPE.
- Carga inicial com especialidades e horários padrão.

## Tecnologias Utilizadas

- Python 3.12+
- Django 6.0.4
- SQLite
- HTML5
- CSS3
- Django Templates
- Django Admin

## Especialidades Padrão

A migração inicial carrega automaticamente as seguintes especialidades:

| Especialidade | Médico(a) | Horários |
| --- | --- | --- |
| Cardiologia | Dr. João | 08:00, 09:00, 10:00 |
| Pediatria | Dra. Maria | 13:00, 14:00, 15:00 |
| Ortopedia | Dr. Lucas | 09:30, 10:30, 11:30 |
| Dermatologia | Dra. Ana | 08:30, 09:30, 10:30 |
| Ginecologia | Dra. Paula | 14:00, 15:00, 16:00 |
| Clínico Geral | Dr. Roberto | 07:00, 08:00, 09:00 |

## Estrutura do Projeto

```text
complexo_hospitalar_framework_upe/
├── complexo_hospitalar_framework_upe/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── teleagendamento/
│   ├── management/
│   │   └── commands/
│   │       └── carregar_especialidades.py
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── static/
│   │   └── teleagendamento/
│   │       ├── images/
│   │       │   └── logo-upe.jpeg
│   │       └── styles.css
│   ├── templates/
│   │   └── teleagendamento/
│   │       ├── base.html
│   │       ├── consulta_confirm_delete.html
│   │       ├── consulta_form.html
│   │       └── consulta_list.html
│   ├── admin.py
│   ├── apps.py
│   ├── data.py
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── .env.example
├── .gitignore
├── manage.py
├── README.md
└── requirements.txt
```

## Como Executar Localmente

Clone o repositório:

```bash
git clone <url-do-repositorio>
cd complexo_hospitalar_framework_upe
```

Crie e ative um ambiente virtual:

```bash
python3 -m venv venv
source venv/bin/activate
```

Instale as dependências:

```bash
python3 -m pip install -r requirements.txt
```

Execute as migrações:

```bash
python3 manage.py migrate
```

Inicie o servidor:

```bash
python3 manage.py runserver
```

Acesse no navegador:

```text
http://127.0.0.1:8000/
```

## Variáveis de Ambiente

O projeto possui valores padrão para desenvolvimento local, mas em produção é recomendado configurar variáveis de ambiente.

Use o arquivo `.env.example` como referência:

```bash
DJANGO_SECRET_KEY=troque-esta-chave-em-producao
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
```

Exemplo de configuração em ambiente Linux:

```bash
export DJANGO_SECRET_KEY="sua-chave-secreta"
export DJANGO_DEBUG="False"
export DJANGO_ALLOWED_HOSTS="seudominio.com,www.seudominio.com"
```

## Painel Administrativo

O Django Admin está disponível em:

```text
http://127.0.0.1:8000/admin/
```

Para criar um usuário administrador:

```bash
python3 manage.py createsuperuser
```

No painel administrativo é possível gerenciar:

- Especialidades.
- Horários disponíveis.
- Consultas agendadas.
- Usuários e permissões do Django.

## Carga Inicial de Dados

As especialidades e horários padrão são criados automaticamente pela migração inicial.

Se precisar recarregar esses dados manualmente, execute:

```bash
python3 manage.py carregar_especialidades
```

O comando é seguro para executar mais de uma vez, pois usa criação idempotente e evita duplicidade.

## Testes

Para executar a suíte de testes:

```bash
python3 manage.py test
```

Os testes cobrem:

- Normalização do nome do paciente.
- Bloqueio de horário já ocupado.
- Bloqueio de horário fora do catálogo da especialidade.
- Atualização de consulta mantendo o próprio horário.
- Renderização da página inicial.
- Criação de consulta pelo formulário web.

## Regras de Negócio

Uma consulta é composta por:

- Paciente.
- Especialidade.
- Data.
- Hora.
- Observações opcionais.

O sistema valida automaticamente:

- O nome do paciente não pode ser vazio.
- O horário precisa pertencer à grade da especialidade, quando houver grade cadastrada.
- Uma especialidade não pode ter duas consultas na mesma data e hora.
- Ao atualizar uma consulta, o próprio horário atual continua permitido.
- Se o paciente já tiver outro agendamento, o sistema exibe um aviso.

## Comandos Úteis

Criar migrações após alterar modelos:

```bash
python3 manage.py makemigrations
```

Aplicar migrações:

```bash
python3 manage.py migrate
```

Verificar problemas de configuração:

```bash
python3 manage.py check
```

Criar administrador:

```bash
python3 manage.py createsuperuser
```

Executar testes:

```bash
python3 manage.py test
```

## Próximas Melhorias

- Filtro de consultas por data, paciente e especialidade.
- Autenticação obrigatória para uso da agenda.
- Dashboard com indicadores de consultas por especialidade.
- Exportação da agenda em PDF ou CSV.
- API REST para integração com outros sistemas.
- Deploy em serviço cloud.

## Autor

Desenvolvido por Erlon Matheus como projeto de estudo e portfólio em Python, Django e desenvolvimento web.
