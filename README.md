# Complexo Hospitalar UPE em Django

Versão web do sistema de teleagendamento hospitalar, migrada do projeto Python de terminal para Django.

## Funcionalidades

- cadastrar consultas
- listar agendamentos
- alterar/remarcar consultas
- desmarcar consultas
- validar conflitos de horário por especialidade, data e hora
- avisar quando o paciente já possui consulta
- gerenciar especialidades, médicos e horários pelo Django Admin

## Como executar

```bash
python3 -m pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver
```

Depois acesse:

```text
http://127.0.0.1:8000/
```

As especialidades e horários padrão são carregados pela migração inicial. Se precisar recarregar a grade manualmente:

```bash
python3 manage.py carregar_especialidades
```

## Antes de publicar no GitHub

Não versionar arquivos locais/sensíveis como `db.sqlite3`, `venv/`, `.env` e `__pycache__/`.
O projeto já possui um `.gitignore` com essas regras.

Para ambientes fora do desenvolvimento local, configure as variáveis:

```bash
export DJANGO_SECRET_KEY="sua-chave-secreta"
export DJANGO_DEBUG="False"
export DJANGO_ALLOWED_HOSTS="seudominio.com,www.seudominio.com"
```
