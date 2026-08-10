# -*- coding: utf-8 -*-
"""
Aplicacao web Flask: pesquisa de vagas de emprego em Portugal, agregando
varias fontes (scrapers/adaptadores), com extracao estruturada via IA
(ou heuristica) para cada vaga.

Correr localmente:
    pip install -r requirements.txt
    python app.py

Depois abrir http://127.0.0.1:5000
"""

import logging
import os

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify, render_template, request

from config import CATEGORIAS, ZONAS, MAX_RESULTADOS_POR_FONTE
from scrapers import AVAILABLE_SCRAPERS
from ai.extractor import extract_structured

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("app")

app = Flask(__name__)


def _find_categoria(categoria_id):
    for c in CATEGORIAS:
        if c["id"] == categoria_id:
            return c
    return None


def _find_zona(zona_nome):
    for z in ZONAS:
        if z["nome"] == zona_nome:
            return z
    return None


def _dedupe(jobs):
    seen = set()
    unique = []
    for job in jobs:
        key = job.get("url")
        if key and key not in seen:
            seen.add(key)
            unique.append(job)
    return unique


@app.route("/")
def index():
    return render_template("index.html", categorias=CATEGORIAS, zonas=ZONAS)


@app.route("/api/search")
def api_search():
    categoria_id = request.args.get("categoria", "")
    zona_nome = request.args.get("zona", "Todas as zonas")

    categoria = _find_categoria(categoria_id)
    zona = _find_zona(zona_nome) or {"nome": zona_nome, "itjobs_id": None}

    if categoria is None:
        return jsonify({"error": "Categoria invalida."}), 400

    all_jobs = []
    errors = []

    for name, module in AVAILABLE_SCRAPERS.items():
        try:
            jobs = module.search(categoria, zona, limit=MAX_RESULTADOS_POR_FONTE)
            all_jobs.extend(jobs)
        except Exception as exc:
            logger.exception("Erro na fonte %s", name)
            errors.append(f"{name}: {exc}")

    all_jobs = _dedupe(all_jobs)

    enriched = []
    for job in all_jobs:
        structured = extract_structured(job.get("title", ""), job.get("raw_text", ""))
        enriched.append({
            "source": job.get("source"),
            "title": job.get("title"),
            "company": job.get("company") or "nao especificado",
            "location": job.get("location") or "nao especificado",
            "url": job.get("url"),
            "published_at": job.get("published_at") or "nao especificado",
            "requirements": structured["requirements"],
            "responsibilities": structured["responsibilities"],
            "salary_benefits": job.get("salary_hint") or structured["salary_benefits"],
        })

    return jsonify({
        "count": len(enriched),
        "results": enriched,
        "errors": errors,
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "1") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)
