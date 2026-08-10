# Pesquisa de Vagas de Emprego — Portugal (MVP)

Aplicacao web para pesquisar vagas de emprego em Portugal por categoria e
zona, agregando varias fontes e apresentando cada vaga ja estruturada
(empresa, localizacao, requisitos, funcoes, salario/beneficios, link
original).

## O que esta incluido no MVP

- Interface web (Flask + HTML/CSS/JS simples): dropdown de categoria,
  dropdown de zona, botao "Pesquisar", resultados em cartoes.
- Duas fontes de vagas: Net-Empregos (scraping leve, sem chave) e ITJobs
  (API oficial, chave gratuita opcional em https://www.itjobs.pt/api).
- Extracao estruturada por IA, com fallback automatico:
  1. Usa Claude (Anthropic) se ANTHROPIC_API_KEY estiver definida;
  2. senao usa Gemini (Google) se GEMINI_API_KEY estiver definida;
  3. senao usa um extrator heuristico local (regex + palavras-chave em
     portugues) - funciona sem qualquer chave de API, sem custos.
- Campos em falta sao sempre apresentados como "nao especificado".
- Estrutura pronta para adicionar mais fontes (scrapers/) e a futura
  integracao com Notion (integrations/notion_export.py).

### Fontes consideradas mas nao incluidas no MVP

- LinkedIn / Indeed: nao tem API publica gratuita de pesquisa de vagas
  para terceiros; scraping direto viola os Termos de Servico.
- Sapo Emprego: o site carrega resultados via JavaScript (SPA), pelo que
  scraping leve nao consegue ler os resultados.

## Como correr localmente (gratis)

```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python app.py
```

Depois abre http://127.0.0.1:5000 no browser.

## Deploy gratuito na web (Render.com)

1. Repositorio ja esta no GitHub.
2. Em render.com -> New -> Web Service -> liga o repositorio.
3. Build command: pip install -r requirements.txt
4. Start command: gunicorn app:app
5. Define as variaveis de ambiente (do .env) na seccao Environment.
6. Plano Free.

## Estrutura do projeto

```
app.py
config.py
requirements.txt
.env.example
scrapers/
ai/
integrations/
templates/
static/
```
