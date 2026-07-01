"""
Pacote de configuração: leds_cancer_backend
===========================================

Contém as configurações centrais do projeto Django.

Arquivos
--------
- ``settings.py`` — configurações globais carregadas via ``python-decouple``
  (variáveis sensíveis em ``.env``).
- ``urls.py``     — roteamento raiz; agrega as URLs dos apps ``authentication``,
  ``patients`` e ``exams``, além da documentação automática (Swagger / ReDoc).
- ``wsgi.py``     — ponto de entrada WSGI para servidores de produção.
- ``asgi.py``     — ponto de entrada ASGI para servidores assíncronos.

Principais configurações
-------------------------
- **Autenticação**: JWT via ``djangorestframework-simplejwt``.
  Access token expira em 30 min (configurável por ``JWT_ACCESS_TOKEN_LIFETIME_MINUTES``).
  Refresh token expira em 7 dias (configurável por ``JWT_REFRESH_TOKEN_LIFETIME_DAYS``).
- **Banco de dados**: SQLite por padrão; PostgreSQL (ou qualquer banco
  suportado pelo ``dj-database-url``) se a variável ``DATABASE_URL`` for
  definida no ``.env``.
- **Arquivos de mídia**: armazenados em ``media/`` (servidos pelo Django
  apenas em ambiente de desenvolvimento; em produção deve-se usar um
  servidor de arquivos dedicado).
- **CORS**: origens permitidas definidas por ``CORS_ALLOWED_ORIGINS`` no
  ``.env`` (padrão: ``http://localhost:5173``).
- **Documentação da API**: gerada automaticamente pelo ``drf-spectacular``
  e acessível em:

  =====================================  ==========================================
  Rota                                   Descrição
  =====================================  ==========================================
  ``/api/schema/``                       Schema OpenAPI (JSON/YAML)
  ``/api/docs/``                         Interface Swagger UI
  ``/api/redoc/``                        Interface ReDoc
  =====================================  ==========================================
"""
