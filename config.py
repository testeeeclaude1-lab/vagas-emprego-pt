# -*- coding: utf-8 -*-
"""
Configuracao central da aplicacao: categorias de pesquisa, zonas/distritos
de Portugal e definicoes gerais. Edita este ficheiro para adicionar ou
remover categorias e zonas sem tocar no resto do codigo.
"""

CATEGORIAS = [
    {"id": "design-grafico", "nome": "Design Grafico", "keywords": ["design grafico", "designer grafico"]},
    {"id": "marketing-digital", "nome": "Marketing Digital", "keywords": ["marketing digital", "gestor de marketing digital"]},
    {"id": "multimedia", "nome": "Multimedia", "keywords": ["multimedia", "motion design", "video editor"]},
    {"id": "informatica", "nome": "Informatica / Programacao", "keywords": ["programador", "developer", "informatica"]},
    {"id": "comunicacao", "nome": "Comunicacao / Social Media", "keywords": ["social media", "comunicacao", "community manager"]},
    {"id": "fotografia", "nome": "Fotografia / Video", "keywords": ["fotografia", "videografo", "video maker"]},
    {"id": "ux-ui", "nome": "UX/UI Design", "keywords": ["ux design", "ui design", "product designer"]},
    {"id": "publicidade", "nome": "Publicidade", "keywords": ["publicidade", "advertising"]},
]

ZONAS = [
    {"nome": "Todas as zonas", "itjobs_id": None},
    {"nome": "Lisboa", "itjobs_id": 14},
    {"nome": "Porto", "itjobs_id": 18},
    {"nome": "Braga", "itjobs_id": 4},
    {"nome": "Aveiro", "itjobs_id": 1},
    {"nome": "Coimbra", "itjobs_id": 8},
    {"nome": "Setubal", "itjobs_id": 17},
    {"nome": "Faro", "itjobs_id": 9},
    {"nome": "Leiria", "itjobs_id": 13},
    {"nome": "Santarem", "itjobs_id": 20},
    {"nome": "Viseu", "itjobs_id": 16},
    {"nome": "Viana do Castelo", "itjobs_id": 22},
    {"nome": "Vila Real", "itjobs_id": 21},
    {"nome": "Braganca", "itjobs_id": 5},
    {"nome": "Guarda", "itjobs_id": 11},
    {"nome": "Castelo Branco", "itjobs_id": 6},
    {"nome": "Portalegre", "itjobs_id": 12},
    {"nome": "Evora", "itjobs_id": 10},
    {"nome": "Beja", "itjobs_id": 3},
    {"nome": "Madeira", "itjobs_id": 15},
    {"nome": "Acores", "itjobs_id": 2},
    {"nome": "Remoto / Internacional", "itjobs_id": 29},
]

MAX_RESULTADOS_POR_FONTE = 12

USER_AGENT = (
    "Mozilla/5.0 (compatible; PesquisaVagasPT/1.0; "
    "+https://github.com/) AppleWebKit/537.36"
)

REQUEST_TIMEOUT = 10
