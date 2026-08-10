# -*- coding: utf-8 -*-
"""
Placeholder para a futura integracao com o Notion (fase 2 do projeto).

Quando quiseres ativar a exportacao de vagas para uma base de dados no
Notion:

  1. pip install notion-client
  2. Cria uma integracao em https://www.notion.so/my-integrations e obtem
     um NOTION_TOKEN.
  3. Partilha a base de dados de destino com essa integracao e copia o
     NOTION_DATABASE_ID.
  4. Implementa export_job() abaixo a criar uma pagina na base de dados
     com as propriedades correspondentes aos campos do job.
  5. Expoe um endpoint em app.py e liga-o a um botao "Exportar para Notion"
     em cada cartao do frontend.
"""

import os


def export_job(job: dict):
    """Exporta uma vaga (ja estruturada) para uma base de dados do Notion.

    Nao implementado no MVP - serve apenas de ponto de extensao.
    """
    token = os.environ.get("NOTION_TOKEN")
    database_id = os.environ.get("NOTION_DATABASE_ID")

    if not token or not database_id:
        raise RuntimeError(
            "Integracao com o Notion ainda nao configurada. Define "
            "NOTION_TOKEN e NOTION_DATABASE_ID no .env."
        )

    raise NotImplementedError(
        "Exportacao para o Notion fica para uma fase posterior do projeto."
    )
