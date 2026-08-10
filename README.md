# Pesquisa de Vagas de Emprego -- Portugal (MVP)

Aplicacao web para pesquisar vagas de emprego em Portugal por categoria e
zona, agregando varias fontes e apresentando cada vaga ja estruturada
(empresa, localizacao, requisitos, funcoes, salario/beneficios, link
original).

## O que esta incluido no MVP

- **Interface web** (Flask + HTML/CSS/JS simples): dropdown de categoria,
  dropdown de zona, botao "Pesquisar", resultados em cartoes.
- **Tres fontes de vagas**, escolhidas por serem as mais simples de
  integrar sem scraping agressivo:
  - **Net-Empregos** -- scraping leve da pagina publica de resultados
    (sem login, sem JS, respeitando um User-Agent identificavel). Nota:
    em producao no Render, este site bloqueia o IP do servidor (devolve a
    pagina de login em vez dos resultados) -- funciona normalmente quando
    corres a app localmente, na tua rede de casa. Ver "Limitacoes" abaixo.
  - **ITJobs** -- via API publica oficial (https://www.itjobs.pt/api/docs)
    (precisa de uma chave gratuita -- ver abaixo). Fica focado em
    tecnologia/IT, mas cobre bem categorias como Multimedia.
  - **Jooble** -- via API REST oficial (https://jooble.org/api/about)
    (precisa de uma chave gratuita, aprovacao manual). E um agregador que
    recolhe vagas de centenas de sites portugueses, cobrindo todas as
    categorias (marketing, design, fotografia, etc.), nao so IT.
- **Extracao estruturada por IA**, com fallback automatico:
  1. Usa Claude (Anthropic) se `ANTHROPIC_API_KEY` estiver definida;
  2. senao usa Gemini (Google) se `GEMINI_API_KEY` estiver definida;
  3. senao usa um **extrator heuristico local** (regex + palavras-chave em
     portugues) -- funciona sem qualquer chave de API, sem custos.
- Campos em falta sao sempre apresentados como **"nao especificado"**.
- Estrutura pronta para adicionar mais fontes (`scrapers/`) e a futura
  integracao com Notion (`integrations/notion_export.py`).

### Fontes consideradas mas nao incluidas no MVP

- **LinkedIn**: nao tem API publica gratuita de pesquisa de vagas para
  terceiros; fazer scraping direto viola os Termos de Servico e exigiria
  contornar protecoes anti-bot fortes -- optamos por nao o fazer. Nota: a
  Jooble (fonte acima) por vezes agrega vagas que tambem foram publicadas
  no LinkedIn pelo empregador original, mas via a API oficial da Jooble.
- **Sapo Emprego**: o site atual carrega os resultados via JavaScript
  (aplicacao de pagina unica), pelo que scraping "leve" (sem browser) nao
  consegue ler os resultados. Pode ser adicionado no futuro com um adaptador
  baseado em browser headless, se fizer sentido.

### Limitacao conhecida: Net-Empregos em producao (Render)

O Net-Empregos bloqueia pedidos vindos do IP do plano gratuito do Render
(devolve uma pagina de login/reCAPTCHA em vez dos resultados de pesquisa).
Isto **nao acontece** quando corres a aplicacao localmente no teu
computador -- nesse caso o Net-Empregos funciona normalmente. Por respeitar
os Termos de Servico do site, nao tentamos contornar este bloqueio (sem
proxies, sem rotacao de IP, sem falsificacao de headers).

Se quiseres ter o Net-Empregos incluido nos resultados, a unica forma
gratuita e correta e correr a app localmente (ver seccao seguinte) -- o
resto (ITJobs, Jooble) funciona tanto localmente como no site publicado.

## Levar este projeto para outro computador

Como o codigo esta no GitHub (`https://github.com/testeeeclaude1-lab/vagas-emprego-pt`),
basta em qualquer PC novo:

```bash
git clone https://github.com/testeeeclaude1-lab/vagas-emprego-pt.git
cd vagas-emprego-pt
```

e seguir os passos abaixo ("Como correr localmente"). As unicas coisas que
nao vem no repositorio (por seguranca) sao as chaves de API -- cria de novo
o ficheiro `.env` a partir do `.env.example` e cola la as tuas chaves
(`ITJOBS_API_KEY`, `JOOBLE_API_KEY`, etc.). Guarda essas chaves num local
seguro (ex. gestor de password) para as teres a mao ao mudar de maquina.

## Como correr localmente (gratis)

```bash
# 1. Criar ambiente virtual (opcional mas recomendado)
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. (Opcional) configurar chaves de API
cp .env.example .env
# edita o .env e preenche ITJOBS_API_KEY / JOOBLE_API_KEY / ANTHROPIC_API_KEY / GEMINI_API_KEY
# se quiseres ativar essas fontes/funcionalidades. Sem nenhuma chave, a
# app funciona a mesma com Net-Empregos + extracao heuristica.

# 4. Correr
python app.py
```

Depois abre **http://127.0.0.1:5000** no browser.

## Deploy gratuito na web

Qualquer um destes servicos tem um plano gratuito suficiente para este
projeto (Flask simples, baixo trafego):

### Render.com (recomendado)
1. Cria um repositorio Git com estes ficheiros e faz push para o GitHub.
2. Em render.com -> **New -> Web Service** -> liga o repositorio.
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn app:app`
5. Define as variaveis de ambiente (do `.env`) na seccao "Environment".
6. Plano **Free** -- o servico "adormece" apos inatividade e demora alguns
   segundos a acordar no pedido seguinte, mas nao tem custo.

### Railway.app / Fly.io
Processo semelhante: build a partir do `requirements.txt`, start command
`gunicorn app:app`, variaveis de ambiente no dashboard. Ambos tem planos
gratuitos com limites mensais.

## Como adicionar uma nova categoria ou zona

Edita `config.py` -- nao e preciso tocar em mais nenhum ficheiro:

```python
CATEGORIAS = [
    {"id": "novo-id", "nome": "Nome Visivel", "keywords": ["palavra-chave 1", "palavra-chave 2"]},
    ...
]
```

## Como adicionar uma nova fonte de vagas

1. Cria `scrapers/novo_site.py` com uma funcao:
   ```python
   def search(categoria: dict, zona: dict, limit: int = 12) -> list[dict]:
       ...
   ```
   devolvendo uma lista de dicionarios com as chaves: `source`, `title`,
   `company`, `location`, `url`, `published_at`, `raw_text`.
2. Regista o modulo em `scrapers/__init__.py` (`AVAILABLE_SCRAPERS`).
3. Da preferencia a uma API/RSS oficial sempre que exista; so faz scraping
   HTML de paginas publicas, sem login e sem contornar protecoes anti-bot,
   e confirma os Termos de Servico do site antes de o ligar em producao.

## Notas importantes

- Este projeto respeita os Termos de Servico das fontes ao dar preferencia
  a APIs/RSS oficiais e ao limitar o volume de pedidos por pesquisa
  (`MAX_RESULTADOS_POR_FONTE` em `config.py`).
- A integracao com o Notion fica preparada em
  `integrations/notion_export.py`, mas nao esta ativa nesta fase.

## Estrutura do projeto

```
.
├── app.py                     # Flask: rotas / e /api/search
├── config.py                  # categorias, zonas, definicoes
├── requirements.txt
├── .env.example
├── scrapers/
│   ├── __init__.py            # registo das fontes disponiveis
│   ├── base.py                # helpers HTTP partilhados
│   ├── net_empregos.py        # adaptador Net-Empregos (scraping leve)
│   ├── itjobs.py               # adaptador ITJobs (API oficial)
│   └── jooble.py               # adaptador Jooble (API oficial, agregador)
├── ai/
│   └── extractor.py           # extracao estruturada (IA + fallback heuristico)
├── integrations/
│   └── notion_export.py       # placeholder para fase 2
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```
