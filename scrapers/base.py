# -*- coding: utf-8 -*-
"""Utilitarios partilhados pelos adaptadores de scraping."""

import logging
import requests

from config import USER_AGENT, REQUEST_TIMEOUT

logger = logging.getLogger("scrapers")

# Sessao HTTP partilhada: alguns sites (ex. Net-Empregos) só devolvem a
# pagina de resultados real se houver uma sessao/cookies validos, obtidos
# ao visitar primeiro a homepage. Reutilizamos a mesma sessao entre pedidos.
SESSION = requests.Session()
SESSION.headers.update({
    "User-Agent": USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-PT,pt;q=0.9,en;q=0.8",
})


def safe_get(url, params=None, headers=None, timeout=REQUEST_TIMEOUT):
    """GET defensivo: nunca levanta exceção para fora, devolve None em erro."""
    try:
        resp = SESSION.get(url, params=params, headers=headers, timeout=timeout)
        resp.raise_for_status()
        return resp
    except requests.RequestException as exc:
        logger.warning("Falha ao aceder a %s: %s", url, exc)
        return None


def warm_up(url):
    """Visita uma pagina apenas para obter cookies de sessao validos."""
    try:
        SESSION.get(url, timeout=REQUEST_TIMEOUT)
    except requests.RequestException as exc:
        logger.warning("Falha no warm-up de %s: %s", url, exc)


def normalize(text):
    if not text:
        return ""
    return " ".join(text.split()).strip()
