# -*- coding: utf-8 -*-
"""Utilitarios partilhados pelos adaptadores de scraping."""

import logging
import requests

from config import USER_AGENT, REQUEST_TIMEOUT

logger = logging.getLogger("scrapers")


def safe_get(url, params=None, headers=None, timeout=REQUEST_TIMEOUT):
    final_headers = {"User-Agent": USER_AGENT}
    if headers:
        final_headers.update(headers)
    try:
        resp = requests.get(url, params=params, headers=final_headers, timeout=timeout)
        resp.raise_for_status()
        return resp
    except requests.RequestException as exc:
        logger.warning("Falha ao aceder a %s: %s", url, exc)
        return None


def normalize(text):
    if not text:
        return ""
    return " ".join(text.split()).strip()
