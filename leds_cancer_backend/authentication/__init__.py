"""
Módulo: authentication
======================

Responsável por todo o ciclo de autenticação e gerenciamento de usuários
do sistema LEDS Cancer.

Modelo principal
----------------
- **User** (herda de ``AbstractUser``): usa ``username`` como identificador
  de login, mas também aceita ``email`` ou ``CRM`` via o serializer
  customizado. Novos usuários são criados com ``is_active=False`` e só
  passam a ter acesso após aprovação manual de um administrador.

Papéis de usuário (``UserRole``)
---------------------------------
- ``medico``       — Médico(a)
- ``tecnico``      — Técnico(a)
- ``administrador``— Administrador(a)

Endpoints expostos (prefixo ``/api/``)
---------------------------------------
============================================  =======  ==============================================
Rota                                          Método   Descrição
============================================  =======  ==============================================
``auth/token/``                               POST     Login via e-mail **ou** CRM; retorna JWT
``auth/token/refresh/``                       POST     Renova o access token com o refresh token
``auth/register/``                            POST     Cadastro público; conta fica pendente
``auth/me/``                                  GET      Dados do usuário autenticado
``auth/me/update/``                           PUT/PATCH Atualiza nome, e-mail e/ou CRM
``auth/me/password/``                         POST     Troca de senha (exige senha atual)
============================================  =======  ==============================================

Componentes internos
--------------------
- ``UserRepository``         — camada de acesso a dados; as views não chamam
  ``User.objects`` diretamente.
- ``CustomTokenObtainPairSerializer`` — sobrescreve o login JWT para aceitar
  ``identifier`` (e-mail ou CRM) em vez de ``username``.
- ``RegisterSerializer``     — valida e cria o usuário com ``is_active=False``.
- ``UpdateProfileSerializer``— atualiza campos de perfil com validação de
  unicidade.
- ``UpdatePasswordSerializer``— valida senha atual antes de permitir a troca.
"""
