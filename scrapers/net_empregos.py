# -*- coding: utf-8 -*-
"""
Adaptador para o Net-Empregos (https://www.net-empregos.com).
Scraping leve da pagina de resultados publica (sem login, sem JS,
respeitando um User-Agent identificavel e um limite de pedidos por
pesquisa).
"""
import re
from bs4 import BeautifulSoup
from .base import safe_get, normalize, warm_up
SOURCE_NAME = "Net-Empregos"
BASE_URL = "https://www.net-empregos.com"
SEARCH_URL = "https://www.net-empregos.com/pesquisa-empregos.asp"
JOB_LINK_RE = re.compile(r"^/\d{5,}/[a-z0-9\-]+/?$", re.IGNORECASE)
DATE_RE = re.compile(r"^\d{1,2}-\d{1,2}-\d{4}$")

# Palavras demasiado genericas para pesquisar sozinhas (preposicoes, artigos).
_STOPWORDS = {
    "de", "da", "do", "das", "dos", "e", "em", "para", "com", "a", "o",
    "as", "os", "no", "na", "nos", "nas", "um", "uma", "ou", "por",
}

# Termos que indicam que a vaga se aplica ao pais inteiro (nao a uma zona
# especifica), pelo que deve aparecer mesmo quando o utilizador filtra por
# uma zona concreta (ex: Braga).
_NATIONWIDE_MARKERS = (
    "todas as zonas", "todo o pais", "todo o país", "nacional",
    "remoto", "remote", "portugal inteiro",
)

_warmed_up = False


def _is_nationwide(location):
    """Devolve True se a localizacao indicar que a vaga se aplica a todo o
    pais (ex: "( Todas as Zonas )"), nao devendo ser excluida por um filtro
    de zona especifica."""
    if not location:
        return False
    loc = location.lower()
    return any(marker in loc for marker in _NATIONWIDE_MARKERS)


def _expand_keywords(keywords):
    """
    Expande a lista de palavras-chave: para alem das frases originais,
    acrescenta tambem as palavras individuais de cada frase (ex: "marketing
    digital" -> tambem pesquisa "marketing" e "digital" separadamente).

    Isto porque o motor de pesquisa do Net-Empregos exige que TODAS as
    palavras da pesquisa apareçam na vaga (é uma pesquisa "E", nao "OU"),
    por isso uma frase composta pode ser demasiado restritiva e deixar de
    fora vagas relevantes que só têm uma das palavras.

    Mantém a ordem: frases originais primeiro, depois as palavras novas
    que ainda não tinham aparecido, sem duplicados.
    """
    ordered = []
    seen = set()

    for phrase in keywords:
        phrase_norm = phrase.strip().lower()
        if phrase_norm and phrase_norm not in seen:
            seen.add(phrase_norm)
            ordered.append(phrase)

    for phrase in keywords:
        for word in phrase.strip().lower().split():
            if len(word) > 2 and word not in _STOPWORDS and word not in seen:
                seen.add(word)
                ordered.append(word)

    return ordered


def _ensure_session():
    """Visita a homepage uma vez por processo para obter cookies validos
    antes de pedir a pagina de resultados (o site devolve uma pagina
    diferente - login/homepage - sem uma sessao valida)."""
    global _warmed_up
    if not _warmed_up:
        warm_up(BASE_URL + "/")
        _warmed_up = True


def _find_job_links(soup):
    seen = set()
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        path = href.replace(BASE_URL, "")
        if JOB_LINK_RE.match(path):
            full_url = BASE_URL + path if path.startswith("/") else href
            if full_url not in seen:
                seen.add(full_url)
                links.append((full_url, a))
    return links


def _extract_card_fields(anchor):
    container = anchor
    for _ in range(6):
        if container.parent is None:
            break
        container = container.parent
        text_items = [normalize(li.get_text(" ")) for li in container.find_all("li")]
        text_items = [t for t in text_items if t]
        if len(text_items) >= 2:
            return container, text_items
    return container, []


def _parse_card(url, anchor):
    title = normalize(anchor.get_text(" "))
    container, items = _extract_card_fields(anchor)
    date = None
    location = None
    category = None
    company = None
    remaining = []
    for item in items:
        if DATE_RE.match(item):
            date = item
        else:
            remaining.append(item)
    if len(remaining) >= 1:
        location = remaining[0]
    if len(remaining) >= 2:
        category = remaining[1]
    if len(remaining) >= 3:
        company = remaining[-1]
    if not title:
        heading = container.find(["h2", "h3"]) if container else None
        if heading:
            title = normalize(heading.get_text(" "))
    return {
        "source": SOURCE_NAME,
        "title": title or "(titulo nao disponivel)",
        "company": company,
        "location": location,
        "category_hint": category,
        "url": url,
        "published_at": date,
    }


def _fetch_job_detail(url):
    resp = safe_get(url)
    if resp is None:
        return ""
    soup = BeautifulSoup(resp.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    candidates = soup.find_all(["div", "article", "section"])
    best_text = ""
    for c in candidates:
        text = normalize(c.get_text(" "))
        if len(text) > len(best_text) and len(text) < 20000:
            best_text = text
    if not best_text:
        best_text = normalize(soup.get_text(" "))
    return best_text


def search(categoria, zona, limit=12, max_pages=6, fetch_details=True):
    """
    categoria: dict de config.CATEGORIAS
    zona: dict de config.ZONAS

    Percorre TODAS as palavras-chave da categoria (nao so a primeira) e,
    para cada uma, todas as paginas de resultados ate ``max_pages`` (ou ate
    a pagina deixar de ter vagas), juntando os resultados sem duplicados,
    ate atingir o limite total pedido.
    """
    _ensure_session()
    results = []
    seen_urls = set()
    keywords = _expand_keywords(categoria.get("keywords", [categoria.get("nome", "")]))
    zona_nome = zona.get("nome", "")
    filtro_zona = None if zona_nome.lower().startswith("todas") else zona_nome

    for query in keywords:
        if len(results) >= limit:
            break

        for page in range(1, max_pages + 1):
            params = {"chaves": query}
            if page > 1:
                params["page"] = page

            resp = safe_get(SEARCH_URL, params=params)
            if resp is None:
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            job_links = _find_job_links(soup)
            if not job_links:
                break

            for url, anchor in job_links:
                if url in seen_urls:
                    continue

                card = _parse_card(url, anchor)

                if filtro_zona and not _is_nationwide(card["location"]):
                    if card["location"]:
                        if filtro_zona.lower() not in card["location"].lower():
                            continue
                    else:
                        continue

                seen_urls.add(url)
                results.append(card)
                if len(results) >= limit:
                    break

            if len(results) >= limit:
                break

    if fetch_details:
        for card in results:
            card["raw_text"] = _fetch_job_detail(card["url"])
    else:
        for card in results:
            card["raw_text"] = card["title"]

    return results
