# -*- coding: utf-8 -*-
"""
Adaptador para o ITJobs.pt, usando a API publica oficial
(https://www.itjobs.pt/api/docs). Precisa de uma API key gratuita.
Se a chave nao estiver definida, devolve lista vazia.
"""

import os
from bs4 import BeautifulSoup

from .base import safe_get, normalize

SOURCE_NAME = "ITJobs"
SEARCH_URL = "https://api.itjobs.pt/job/search.json"


def _strip_html(html_body):
    if not html_body:
        return ""
    soup = BeautifulSoup(html_body, "html.parser")
    return normalize(soup.get_text(" "))


def search(categoria, zona, limit=12):
    api_key = os.environ.get("ITJOBS_API_KEY")
    if not api_key:
        return []

    keywords = categoria.get("keywords", [categoria.get("nome", "")])
    query = ",".join(keywords)

    params = {
        "api_key": api_key,
        "q": query,
        "limit": min(limit, 50),
    }
    location_id = zona.get("itjobs_id")
    if location_id:
        params["location"] = location_id

    resp = safe_get(SEARCH_URL, params=params)
    if resp is None:
        return []

    try:
        data = resp.json()
    except ValueError:
        return []

    if "error" in data:
        return []

    results = []
    for job in data.get("results", [])[:limit]:
        company = (job.get("company") or {}).get("name")
        locations = ", ".join(loc.get("name", "") for loc in job.get("locations", []))
        salary_min = job.get("salaryMin")
        salary_max = job.get("salaryMax")
        salary_hint = None
        if salary_min or salary_max:
            salary_hint = f"{salary_min or '?'} - {salary_max or '?'} EUR/ano (bruto)"

        results.append({
            "source": SOURCE_NAME,
            "title": normalize(job.get("title", "")),
            "company": company,
            "location": locations or None,
            "category_hint": None,
            "url": f"https://www.itjobs.pt/oferta/{job.get('slug', '')}",
            "published_at": job.get("publishedAt"),
            "raw_text": _strip_html(job.get("body", "")),
            "salary_hint": salary_hint,
        })

    return results
