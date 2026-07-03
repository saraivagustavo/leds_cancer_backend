# LEDS Cancer — Backend

API REST do sistema de análise de exames de mamografia desenvolvido pelo **LEDS (Laboratório de Engenharia de Software)**. Fornece autenticação, gerenciamento de pacientes, exames e um endpoint seguro de acesso a imagens para serviços externos (ex: modelos de IA).

---

## Tecnologias

| Tecnologia                    | Versão | Função                            |
| ----------------------------- | ------ | --------------------------------- |
| Python                        | 3.12   | Linguagem base                    |
| Django                        | 5.x    | Framework web                     |
| Django REST Framework         | 3.x    | Camada REST                       |
| djangorestframework-simplejwt | —      | Autenticação JWT                  |
| drf-spectacular               | —      | Documentação OpenAPI automática   |
| python-decouple               | —      | Variáveis de ambiente             |
| dj-database-url               | —      | Suporte a PostgreSQL via URL      |
| Pillow                        | —      | Processamento de imagens (upload) |

---

## Arquitetura

O projeto segue o **Repository Pattern**: nenhuma view acessa o ORM diretamente — toda interação com o banco passa por uma classe `*Repository` dedicada.

```
leds_cancer_backend/
├── authentication/       # Usuários, login JWT, perfil
│   ├── models.py         # User (AbstractUser customizado)
│   ├── repositories.py   # UserRepository
│   ├── serializers.py    # Login, registro, perfil, senha
│   ├── views.py          # Endpoints de auth
│   └── urls.py
├── patients/             # Cadastro e gestão de pacientes
│   ├── models.py         # Patient
│   ├── repositories.py   # PatientRepository
│   ├── serializers.py    # List, Detail, Write
│   ├── views.py          # CRUD de pacientes
│   └── urls.py
├── exams/                # Exames de mamografia
│   ├── models.py         # Exam + enums de status/técnica/lado
│   ├── repositories.py   # ExamRepository + contadores dashboard
│   ├── serializers.py    # Listagem, escrita, dashboard, token
│   ├── views.py          # CRUD de exames + dashboard + image token
│   ├── tokens.py         # Geração e validação HMAC (acesso externo)
│   └── urls.py
└── leds_cancer_backend/  # Configuração central
    ├── settings.py
    └── urls.py
```

---

## Configuração e instalação

### 1. Pré-requisitos

- Python 3.12
- `pip` ou `uv`

### 2. Clonar e criar o ambiente virtual

```bash
git clone https://github.com/saraivagustavo/leds_cancer_backend.git
cd leds_cancer_backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### 3. Variáveis de ambiente

Copie `.env.example` para `.env` e preencha os valores:

```bash
cp .env.example .env
```

```dotenv
# Django
SECRET_KEY=sua-chave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=*

# CORS (origens permitidas para o frontend)
CORS_ALLOWED_ORIGINS=http://localhost:5173

# Banco de dados — deixe vazio para SQLite (desenvolvimento)
DATABASE_URL=

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=30
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# Token HMAC para acesso externo a imagens
IMAGE_TOKEN_SECRET=outra-chave-secreta-dedicada
IMAGE_TOKEN_TTL_SECONDS=900
```

> **Produção:** defina `DATABASE_URL` com a string de conexão PostgreSQL e use valores distintos para `SECRET_KEY` e `IMAGE_TOKEN_SECRET`.

### 4. Banco de dados e servidor

```bash
cd leds_cancer_backend   # pasta que contém manage.py
python manage.py migrate
python manage.py runserver
```

### 5. Criar superusuário

```bash
# Opção 1 — interativo
python manage.py createsuperuser

# Opção 2 — script rápido (cria usuário "integracao")
cd ..   # raiz do projeto
python create_admin.py
```

---

## Endpoints da API

A documentação interativa completa está disponível em:

| Interface             | URL                                 |
| --------------------- | ----------------------------------- |
| Swagger UI            | `http://localhost:8000/api/docs/`   |
| ReDoc                 | `http://localhost:8000/api/redoc/`  |
| Schema OpenAPI (JSON) | `http://localhost:8000/api/schema/` |

### Autenticação (`/api/auth/`)

| Método    | Rota                   | Descrição                      | Auth |
| --------- | ---------------------- | ------------------------------ | ---- |
| POST      | `/auth/token/`         | Login por e-mail ou CRM        | ✗    |
| POST      | `/auth/token/refresh/` | Renovar access token           | ✗    |
| POST      | `/auth/register/`      | Cadastro (conta fica pendente) | ✗    |
| GET       | `/auth/me/`            | Dados do usuário logado        | ✓    |
| PUT/PATCH | `/auth/me/update/`     | Atualizar nome, e-mail, CRM    | ✓    |
| POST      | `/auth/me/password/`   | Alterar senha                  | ✓    |
| GET       | `/auth/users/`         | Listar médicos/técnicos ativos | ✓    |

> Novos usuários são criados com `is_active=False`. Um administrador precisa ativá-los pelo painel `/admin/`.

### Pacientes (`/api/patients/`)

| Método    | Rota              | Descrição                     | Auth |
| --------- | ----------------- | ----------------------------- | ---- |
| GET       | `/patients/`      | Listar pacientes (`?search=`) | ✓    |
| POST      | `/patients/`      | Criar paciente                | ✓    |
| GET       | `/patients/{id}/` | Detalhe + lista de exames     | ✓    |
| PUT/PATCH | `/patients/{id}/` | Atualizar paciente            | ✓    |
| DELETE    | `/patients/{id}/` | Remover paciente              | ✓    |

### Exames (`/api/exams/`)

| Método    | Rota                       | Descrição                                           | Auth  |
| --------- | -------------------------- | --------------------------------------------------- | ----- |
| GET       | `/exams/`                  | Listar exames (`?search=`, `?status=`, `?patient=`) | ✓     |
| POST      | `/exams/`                  | Criar exame com upload de imagem (multipart)        | ✓     |
| GET       | `/exams/recent/`           | Últimos exames para o feed (`?limit=N`)             | ✓     |
| GET       | `/exams/{id}/`             | Detalhe do exame                                    | ✓     |
| PUT/PATCH | `/exams/{id}/`             | Atualizar exame                                     | ✓     |
| DELETE    | `/exams/{id}/`             | Remover exame                                       | ✓     |
| POST      | `/exams/{id}/image-token/` | Gerar token HMAC para acesso externo                | ✓     |
| GET       | `/exams/{id}/image/`       | Baixar imagem via token HMAC                        | ✗ JWT |

### Dashboard (`/api/dashboard/`)

| Método | Rota                | Descrição                         | Auth |
| ------ | ------------------- | --------------------------------- | ---- |
| GET    | `/dashboard/stats/` | Contadores dos cards do dashboard | ✓    |

---

## Acesso externo a imagens (HMAC)

Serviços externos (ex: modelos de IA) acessam imagens sem JWT, usando um token HMAC de curta duração:

```
# 1. Frontend solicita o token (requer JWT)
POST /api/exams/{id}/image-token/
→ { "token": "a3f9...", "expires_at": 1782922627 }

# 2. Serviço externo baixa a imagem (sem JWT)
GET /api/exams/{id}/image/?token=a3f9...&expires=1782922627
→ FileResponse (binário da imagem)
```

O token é `HMAC-SHA256(IMAGE_TOKEN_SECRET, "{exam_id}:{expires_ts}")`, stateless e com expiração configurável via `IMAGE_TOKEN_TTL_SECONDS` (padrão: 900 s = 15 min).

---

## Modelos principais

### User

| Campo       | Tipo                        | Descrição                               |
| ----------- | --------------------------- | --------------------------------------- |
| `email`     | EmailField (único)          | Login alternativo ao username           |
| `crm`       | CharField (único, opcional) | Registro profissional                   |
| `role`      | CharField                   | `medico` · `tecnico` · `administrador`  |
| `is_active` | BooleanField                | `False` por padrão (pendente aprovação) |

### Patient

| Campo        | Tipo              | Descrição                      |
| ------------ | ----------------- | ------------------------------ |
| `name`       | CharField         | Nome completo                  |
| `birth_date` | DateField         | Data de nascimento             |
| `cpf`        | CharField (único) | CPF formatado `000.000.000-00` |
| `status`     | CharField         | `ativo` · `inativo`            |

### Exam

| Campo         | Tipo         | Descrição                                             |
| ------------- | ------------ | ----------------------------------------------------- |
| `patient`     | FK → Patient | Paciente do exame (cascade delete)                    |
| `exam_date`   | DateField    | Data de realização                                    |
| `technique`   | CharField    | `digital` · `3d_tomossintese` · `contraste`           |
| `breast_side` | CharField    | `esquerda` · `direita` · `bilateral`                  |
| `image_file`  | ImageField   | Armazenado em `media/exams/images/%Y/%m/`             |
| `status`      | CharField    | `pendente` · `em_analise` · `concluido` · `cancelado` |
| `radiologist` | FK → User    | Profissional que analisou (SET_NULL)                  |

---

## Comandos úteis

```bash
# Dentro de leds_cancer_backend/ (onde está o manage.py)

# Servidor de desenvolvimento
python manage.py runserver

# Migrações
python manage.py makemigrations
python manage.py migrate

# Criar novo app
python manage.py startapp {nome}

# Shell interativo
python manage.py shell
```

---

## Painel administrativo

Acesse `http://localhost:8000/admin/` para:

- Aprovar/desativar usuários
- Inspecionar pacientes e exames
- Gerenciar qualquer modelo diretamente
