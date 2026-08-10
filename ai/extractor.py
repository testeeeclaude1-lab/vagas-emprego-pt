# -*- coding: utf-8 -*-
"""
Extração estruturada de informação de vagas de emprego a partir de texto
em bruto (cada site de emprego formata a descrição de forma diferente).

Estratégia:
  1. Se existir ANTHROPIC_API_KEY no ambiente -> usa a API da Claude (Anthropic).
  2. Senão, se existir GEMINI_API_KEY -> usa a API do Gemini (Google).
  3. Senão -> usa um extrator heurístico local (regex + palavras-chave em
     português), que não precisa de nenhuma chave e funciona offline.

Todas as vias devolvem sempre o mesmo formato:

    {
        "requirements": str,
        "responsibilities": str,
        "salary_benefits": str,
    }

Campos que não sejam encontrados ficam com o valor "não especificado", como
pedido no requisito do projeto.
"""

import json
import logging
import os
import re

NAO_ESPECIFICADO = "não especificado"
logger = logging.getLogger("ai.extractor")

FIELDS = ["requirements", "responsibilities", "salary_benefits"]

PROMPT_TEMPLATE = """Analisa o seguinte anúncio de emprego (em português, de Portugal) e
extrai APENAS estes três campos, em português, cada um como uma LISTA DE
TÓPICOS curtos (não um parágrafo corrido). Cada tópico é uma frase curta e
objetiva. Junta os tópicos com "\\n" (nova linha) dentro da mesma string, no
máximo 5 tópicos por campo.

1. requirements: requisitos/perfil pedido ao candidato (formação, experiência, competências) — um tópico por requisito.
2. responsibilities: funções e responsabilidades do cargo — um tópico por função.
3. salary_benefits: margem salarial e/ou benefícios/vantagens mencionados — um tópico por benefício.

Se um campo não estiver presente no texto, usa exatamente o valor "não especificado".

Responde APENAS com um JSON válido, sem texto adicional, no formato:
{{"requirements": "tópico 1\\ntópico 2", "responsibilities": "...", "salary_benefits": "..."}}

Título da vaga: {title}

Texto do anúncio:
\"\"\"
{body}
\"\"\"
"""


def _empty_result():
    return {field: NAO_ESPECIFICADO for field in FIELDS}


def _safe_json_parse(text):
    text = text.strip()
    # Remove markdown code fences, se existirem
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
        logger.warning("Pacote 'anthropic' não instalado; a usar extrator heurístico.")
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
        logger.warning("Falha na extração via Claude: %s", exc)
        return None


def _extract_with_gemini(title, body, api_key):
    try:
        import google.generativeai as genai
    except ImportError:
        logger.warning("Pacote 'google-generativeai' não instalado; a usar extrator heurístico.")
        return None

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(PROMPT_TEMPLATE.format(title=title, body=body[:6000]))
        return _safe_json_parse(response.text)
    except Exception as exc:
        logger.warning("Falha na extração via Gemini: %s", exc)
        return None


# --- Extrator heurístico (sem IA), usado como fallback --------------------

SECTION_KEYWORDS = {
    "requirements": [
        "requisitos", "perfil pretendido", "perfil do candidato", "procuramos",
        "o que procuramos", "requisitos técnicos", "competências", "formação",
        "quem procuramos", "perfil ideal",
    ],
    "responsibilities": [
        "funções", "responsabilidades", "principais funções", "o que vais fazer",
        "descrição da função", "tarefas", "atividades",
    ],
    "salary_benefits": [
        "salário", "vencimento", "remuneração", "benefícios", "oferecemos",
        "o que oferecemos", "vantagens", "pacote salarial",
    ],
}

SALARY_PATTERN = re.compile(
    r"(\d[\d.,]{2,}\s?(?:€|eur|euros)|(?:€|eur)\s?\d[\d.,]{1,})",
    re.IGNORECASE,
)


def _split_into_sections(text):
    """Divide o texto em blocos, usando cabeçalhos comuns como separadores."""
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


def _to_bullets(text, max_items=5, max_len_per_item=180):
    """Converte um bloco de texto corrido numa lista de tópicos curtos
    (string com um tópico por linha, separados por "\\n"), para que o
    frontend consiga apresentar cada um como um item de lista em vez de
    um parágrafo denso e difícil de ler."""
    if not text:
        return ""

    # Separa por pontuação/marcadores comuns usados nestes anúncios.
    raw_parts = re.split(r"[•·▪\-–]\s+|;\s*|\.\s+(?=[A-ZÀ-Ú])", text)
    parts = [normalize_whitespace(p) for p in raw_parts]
    parts = [p for p in parts if len(p) > 2]

    if not parts:
        parts = [text]

    bullets = []
    for p in parts:
        p = p.strip(" .;:-")
        if not p:
            continue
        if len(p) > max_len_per_item:
            p = p[:max_len_per_item].rsplit(" ", 1)[0] + "…"
        bullets.append(p)
        if len(bullets) >= max_items:
            break

    return "\n".join(bullets)


def normalize_whitespace(s):
    return " ".join(s.split()).strip(" :.-")


def _extract_heuristic(title, body):
    result = _empty_result()
    if not body:
        return result

    sections = _split_into_sections(body)
    for field in FIELDS:
        if field in sections and sections[field]:
            text = sections[field][0][:1200]
            result[field] = _to_bullets(text) or NAO_ESPECIFICADO

    if result["salary_benefits"] == NAO_ESPECIFICADO:
        match = SALARY_PATTERN.search(body)
        if match:
            result["salary_benefits"] = match.group(0)

    return result


# --- Ponto de entrada público ----------------------------------------------

def extract_structured(title, body):
    """Devolve dict com requirements / responsibilities / salary_benefits."""
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
