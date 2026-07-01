"""
Módulo: exams
=============

Responsável pelo gerenciamento de exames de mamografia e pelas
estatísticas do dashboard do sistema LEDS Cancer.

Modelo principal
----------------
- **Exam**: representa um exame de mamografia vinculado a um paciente.
  Suporta upload de imagem (armazenada em ``media/exams/images/<ano>/<mês>/``).

Campos do modelo
----------------
========================  =====================================================
Campo                     Descrição
========================  =====================================================
``patient``               FK para ``Patient`` (cascade delete)
``exam_date``             Data do exame (formato dd/MM/yyyy na API)
``technique``             Técnica utilizada (ver ``ExamTechnique``)
``breast_side``           Lado examinado (ver ``BreastSide``)
``clinical_history``      Histórico clínico (opcional)
``requesting_physician``  Médico solicitante (opcional)
``image_file``            Imagem do exame (upload multipart, opcional)
``status``                Status atual (ver ``ExamStatus``)
``radiologist``           FK para ``User`` — profissional que analisou
``created_at``            Data/hora de criação (automático)
``updated_at``            Data/hora da última atualização (automático)
========================  =====================================================

Enumerações
-----------
- ``ExamStatus``    — ``pendente`` | ``em_analise`` | ``concluido`` | ``cancelado``
- ``ExamTechnique`` — ``digital`` | ``3d_tomossintese`` | ``contraste``
- ``BreastSide``    — ``esquerda`` | ``direita`` | ``bilateral``

Endpoints expostos (prefixo ``/api/``)
---------------------------------------
======================  ===========  ==========================================
Rota                    Método       Descrição
======================  ===========  ==========================================
``exams/``              GET          Lista exames; suporta ``?search=``,
                                     ``?status=`` e ``?patient=``
``exams/``              POST         Cria exame (multipart — aceita imagem)
``exams/recent/``       GET          Últimos exames para o feed do dashboard;
                                     suporta ``?limit=N`` (padrão: 20)
``exams/<id>/``         GET          Detalhe do exame
``exams/<id>/``         PUT / PATCH  Atualização completa ou parcial
``exams/<id>/``         DELETE       Remove o exame
``dashboard/stats/``    GET          Contadores para os cards do dashboard
======================  ===========  ==========================================

Serializers
-----------
- ``ExamListSerializer``            — visão completa usada na listagem e no
  detalhe individual.
- ``ExamWriteSerializer``           — utilizado nas operações de criação e
  atualização; aceita imagem via upload multipart.
- ``ExamSummaryForPatientSerializer``— visão compacta aninhada dentro de
  ``PatientDetailSerializer`` (módulo ``patients``).
- ``RecentExamSerializer``          — visão para o feed de exames recentes
  do dashboard.
- ``DashboardStatsSerializer``      — serializa os contadores do endpoint
  ``/api/dashboard/stats/``.

Dashboard — métricas disponíveis
----------------------------------
- ``today_patients``      — exames com data igual a hoje
- ``pending_exams``       — exames com status ``pendente``
- ``monthly_diagnostics`` — exames do mês corrente
- ``concluded_today``     — exames concluídos hoje

Componentes internos
--------------------
- ``ExamRepository`` — camada de acesso a dados; as views não chamam
  ``Exam.objects`` diretamente. Fornece busca, filtros, contadores para o
  dashboard e operações CRUD completas.
"""
