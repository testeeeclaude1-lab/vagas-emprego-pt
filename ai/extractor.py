# -*- coding: utf-8 -*-
"""
Extracao estruturada de informacao de vagas de emprego a partir de texto
em bruto. Usa Claude (Anthropic) ou Gemini se houver chave de API definida;
caso contrario usa um extrator heuristico local (regex + palavras-chave em
portugues), que funciona offline sem custos.
"""

import json
import logging
import os
import re

NAO_ESPECIFICADO = "nao especificado"
logger = logging.getLogger("ai.extractor")

FIELDS = ["requirements", "responsibilities", "salary_benefits"]

PROMPT_TEMPLATE = """Analisa o seguinte anuncio de emprego (em portugues, de Portugal) e
extrai APENAS estes tres campos, em portugues, de forma resumida (2-4 frases cada):

1. requirements: requisitos/perfil pedido ao candidato (formacao, experiencia, competencias).
2. responsibilities: funcoes e responsabilidades do cargo.
3. salary_benefits: margem salarial e/ou beneficios/vantagens mencionados.

Se um campo nao estiver presente no texto, usa exatamente o valor "nao especificado".

Responde APENAS com um JSON valido, sem texto adicional, no formato:
{{"requirements": "...", "responsibilities": "...", "salary_benefits": "..."}}

Titulo da vaga: {title}

Texto do anuncio:
\"\"\"
{body}
\"\"\"
"""


def _empty_result():
    return {field: NAO_ESPECIFICADO for field in FIELDS}


def _safe_json_parse(text):
    text = text.strip()
    text = re.sub(r"^```(json)?|```$", "", text, flags=re.MULTILINE).strip()
    try:
        data = json.loads(text)
        return {field: (data.get(field) or NAO_ESPECIFICADO).strip() or NAO_ESPECIFICADO for field in FIELDS}
    except (ValueError, AttributeError):
        return None


def _extract_with_claude(title, body, api_key):
    try:
        import anthropic
    except ImportError:
        logger.warning("Pacote 'anthropic' nao instalado; a usar extrator heuristico.")
        return None

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=500,
            messages=[{
                "role": "user",
                "content": PROMPT_TEMPLATE.format(title=title, body=body[:6000]),
            }],
        )
        text = "".join(block.text for block in message.content if hasattr(block, "text"))
        return _safe_json_parse(text)
    except Exception as exc:
        logger.warning("Falha na extracao via Claude: %s", exc)
        return None


def _extract_with_gemini(title, body, api_key):
    try:
        import google.generativeai as genai
    except ImportError:
        logger.warning("Pacote 'google-generativeai' nao instalado; a usar extrator heuristico.")
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(PROMPT_TEMPLATE.format(title=title, body=body[:6000]))
        return _safe_json_parse(response.text)
    except Exception as exc:
        logger.warning("Falha na extracao via Gemini: %s", exc)
        return None


SECTION_KEYWORDS = {
    "requirements": [
        "requisitos", "perfil pretendido", "perfil do candidato", "procuramos",
        "o que procuramos", "requisitos tecnicos", "competencias", "formacao",
        "quem procuramos", "perfil ideal",
    ],
    "responsibilities": [
        "funcoes", "responsabilidades", "principais funcoes", "o que vais fazer",
        "descricao da funcao", "tarefas", "atividades",
    ],
    "salary_benefits": [
        "salario", "vencimento", "remuneracao", "beneficios", "oferecemos",
        "o que oferecemos", "vantagens", "pacote salarial",
    ],
}

SALARY_PATTERN = re.compile(
    r"(\d[\d.,]{2,}\s?(?:€|eur|euros)|(?:€|eur)\s?\d[\d.,]{1,})",
    re.IGNORECASE,
)


def _split_into_sections(text):
    all_keywords = sorted(
        {kw for kws in SECTION_KEYWORDS.values() for kw in kws},
        key=len,
        reverse=True,
    )
    pattern = re.compile(
        r"(" + "|".join(re.escape(k) for k in all_keywords) + r")",
        re.IGNORECASE,
    )
    parts = pattern.split(text)

    sections = {}
    current_field = None
    buffer = []

    def flush():
        if current_field and buffer:
            joined = normalize_whitespace(" ".join(buffer))
            if joined:
                sections.setdefault(current_field, []).append(joined)

    def normalize_whitespace(s):
        return " ".join(s.split()).strip(" :.-")

    for part in parts:
        matched_field = None
        for field, kws in SECTION_KEYWORDS.items():
            if part.strip().lower() in [k.lower() for k in kws]:
                matched_field = field
                break
        if matched_field:
            flush()
            current_field = matched_field
            buffer = []
        else:
            buffer.append(part)
    flush()

    return sections


def _extract_heuristic(title, body):
    result = _empty_result()
    if not body:
        return result

    sections = _split_into_sections(body)
    for field in FIELDS:
        if field in sections and sections[field]:
            text = sections[field][0]
            result[field] = (text[:400] + "...") if len(text) > 400 else text

    if result["salary_benefits"] == NAO_ESPECIFICADO:
        match = SALARY_PATTERN.search(body)
        if match:
            result["salary_benefits"] = match.group(0)

    return result


def extract_structured(title, body):
    if not body:
        return _empty_result()

    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    gemini_key = os.environ.get("GEMINI_API_KEY")

    result = None
    if anthropic_key:
        result = _extract_with_claude(title, body, anthropic_key)
    if result is None and gemini_key:
        result = _extract_with_gemini(title, body, gemini_key)
    if result is None:
        result = _extract_heuristic(title, body)

    for field in FIELDS:
        result.setdefault(field, NAO_ESPECIFICADO)
        if not result[field]:
            result[field] = NAO_ESPECIFICADO

    return result
