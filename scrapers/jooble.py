# -*- coding: utf-8 -*-
"""
Adaptador para a Jooble (https://jooble.org), um agregador de vagas que
recolhe ofertas de centenas de sites de origem em Portugal (incluindo, em
muitos casos, anuncios que tambem aparecem no LinkedIn, Indeed, Net-Empregos,
Sapo Emprego, etc., consoante o que cada empregador publicou onde). Usa a
API REST oficial e gratuita da Jooble -- nao faz scraping.

Precisa de uma API key gratuita: pede-a em https://jooble.org/api/about
(formulario simples com nome, email e site/finalidade -- a aprovacao e
manual e pode demorar algumas horas/dias). Depois define a variavel de
ambiente JOOBLE_API_KEY (ver .env.example).

Se a chave nao estiver definida, este adaptador devolve uma lista vazia (a
aplicacao continua a funcionar com as restantes fontes).

Nota: o plano gratuito da Jooble tem um limite mensal generoso mas finito
(tipicamente algumas centenas de pedidos/mes) -- por isso mantemos o
"limit" por pesquisa baixo (ver MAX_RESULTADOS_POR_FONTE em config.py).
"""

import os

from .base import safe_post, normalize

SOURCE_NAME = "Jooble"
API_URL = "https://jooble.org/api/{key}"


def search(categoria, zona, limit=12):
    api_key = os.environ.get("JOOBLE_API_KEY")
    if not api_key:
        return []

    keywords = categoria.get("keywords", [categoria.get("nome", "")])
    query = " ".join(keywords[:2])

    zona_nome = zona.get("nome", "")
    location = "Portugal" if (not zona_nome or zona_nome == "Todas as zonas") else f"{zona_nome}, Portugal"

    payload = {"keywords": query, "location": location}

    resp = safe_post(API_URL.format(key=api_key), json_body=payload)
    if resp is None:
        return []

    try:
        data = resp.json()
    except ValueError:
        return []

    results = []
    for job in data.get("jobs", [])[:limit]:
        results.append({
            "source": SOURCE_NAME,
            "title": normalize(job.get("title", "")),
            "company": normalize(job.get("company")) or None,
            "location": normalize(job.get("location")) or None,
            "category_hint": None,
            "url": job.get("link"),
            "published_at": job.get("updated"),
            "raw_text": normalize(job.get("snippet", "")),
            "salary_hint": normalize(job.get("salary")) or None,
        })

    return results
