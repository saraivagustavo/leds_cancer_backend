"""
Módulo: patients
================

Responsável pelo cadastro e gerenciamento dos pacientes do sistema
LEDS Cancer.

Modelo principal
----------------
- **Patient**: representa um paciente com dados pessoais e de contato.
  Datas são armazenadas como ``DateField`` e serializadas no formato
  ``dd/MM/yyyy`` para corresponder ao contrato do frontend.

Campos do modelo
----------------
==================  ============================================================
Campo               Descrição
==================  ============================================================
``name``            Nome completo
``birth_date``      Data de nascimento (formato dd/MM/yyyy na API)
``cpf``             CPF (único, com formatação livre)
``phone``           Telefone (opcional)
``email``           E-mail de contato (opcional)
``status``          ``ativo`` | ``inativo``
``created_at``      Data/hora de criação (automático)
``updated_at``      Data/hora da última atualização (automático)
==================  ============================================================

Endpoints expostos (prefixo ``/api/``)
---------------------------------------
============================  ===========  =====================================
Rota                          Método       Descrição
============================  ===========  =====================================
``patients/``                 GET          Lista todos os pacientes;
                                           suporta ``?search=`` (nome/CPF/e-mail)
``patients/``                 POST         Cria um novo paciente
``patients/<id>/``            GET          Detalhe do paciente + exames
``patients/<id>/``            PUT / PATCH  Atualização completa ou parcial
``patients/<id>/``            DELETE       Remove o paciente
============================  ===========  =====================================

Serializers
-----------
- ``PatientListSerializer``   — visão compacta usada na listagem; inclui
  ``age``, ``last_exam`` e ``total_exams`` calculados dinamicamente.
- ``PatientDetailSerializer`` — estende o list com a lista completa de exames
  aninhados (via ``ExamSummaryForPatientSerializer`` do módulo ``exams``).
- ``PatientWriteSerializer``  — utilizado nas operações de criação e
  atualização; valida unicidade do CPF.

Componentes internos
--------------------
- ``PatientRepository`` — camada de acesso a dados; as views não chamam
  ``Patient.objects`` diretamente. Fornece ``search()``, ``get_by_cpf()``,
  ``create()``, ``update()`` e ``delete()``.
"""
