# -*- coding: utf-8 -*-
"""
Pacote de adaptadores ("scrapers") -- um modulo por site de emprego.

Cada adaptador expoe uma funcao:

    search(categoria: dict, zona: dict, limit: int) -> list[dict]

que devolve uma lista de vagas em bruto no seguinte formato:

    {
        "source": "Nome da Fonte",
        "title": str,
        "company": str | None,
        "location": str | None,
        "url": str,
        "published_at": str | None,
        "raw_text": str,   # texto bruto da vaga (descricao completa, se disponivel)
    }

Para adicionar uma nova fonte, cria um novo ficheiro neste pacote seguindo o
mesmo contrato e regista-o em ``AVAILABLE_SCRAPERS`` abaixo.
"""

from . import net_empregos, itjobs, jooble

AVAILABLE_SCRAPERS = {
    "net-empregos": net_empregos,
    "itjobs": itjobs,
    "jooble": jooble,
}
