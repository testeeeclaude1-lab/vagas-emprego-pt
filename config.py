# -*- coding: utf-8 -*-
"""
Configuração central da aplicação: categorias de pesquisa, zonas/distritos
de Portugal e definições gerais. Edita este ficheiro para adicionar ou
remover categorias e zonas sem tocar no resto do código.
"""

# Cada categoria tem um nome apresentado ao utilizador e uma lista de
# palavras-chave usadas para pesquisar nos vários sites (algumas fontes
# só suportam pesquisa por texto livre, por isso usamos vários sinónimos
# e termos descritivos, não só o nome "oficial" do cargo).
CATEGORIAS = [
    {"id": "design-grafico", "nome": "Design Gráfico", "keywords": [
        "design", "design gráfico", "designer gráfico", "graphic designer",
        "banners", "cartazes", "flyers", "criação de artes", "artes gráficas",
        "identidade visual", "branding", "packaging"
    ]},
    {"id": "marketing-digital", "nome": "Marketing Digital", "keywords": [
        "marketing", "marketing digital", "gestor de marketing", "digital marketing",
        "gestão de redes sociais", "campanhas publicitárias", "google ads", "meta ads",
        "email marketing", "growth marketing"
    ]},
    {"id": "multimedia", "nome": "Multimédia", "keywords": [
        "multimédia", "motion design", "video editor", "editor de vídeo",
        "edição de vídeo", "animação", "motion graphics", "produção audiovisual"
    ]},
    {"id": "informatica", "nome": "Informática / Programação", "keywords": [
        "informática", "programador", "developer", "software engineer",
        "desenvolvimento de software", "programação", "web developer", "criação de sites"
    ]},
    {"id": "comunicacao", "nome": "Comunicação / Social Media", "keywords": [
        "comunicação", "social media", "community manager", "content creator",
        "gestão de redes sociais", "criação de conteúdos", "copywriting"
    ]},
    {"id": "fotografia", "nome": "Fotografia / Vídeo", "keywords": [
        "fotografia", "videógrafo", "video maker", "fotógrafo",
        "sessões fotográficas", "edição de fotos", "cobertura de eventos"
    ]},
    {"id": "ux-ui", "nome": "UX/UI Design", "keywords": [
        "ux design", "ui design", "product designer", "ux", "ui",
        "design de interfaces", "protótipos", "figma"
    ]},
    {"id": "publicidade", "nome": "Publicidade", "keywords": [
        "publicidade", "advertising", "criação publicitária", "campanhas de publicidade"
    ]},
]

# Distritos/zonas de Portugal (inclui ids usados pela API do ITJobs, quando
# aplicável). Para o Net-Empregos, a zona é usada como filtro de texto sobre
# a localização apresentada em cada vaga.
ZONAS = [
    {"nome": "Todas as zonas", "itjobs_id": None},
    {"nome": "Lisboa", "itjobs_id": 14},
    {"nome": "Porto", "itjobs_id": 18},
    {"nome": "Braga", "itjobs_id": 4},
    {"nome": "Aveiro", "itjobs_id": 1},
    {"nome": "Coimbra", "itjobs_id": 8},
    {"nome": "Setúbal", "itjobs_id": 17},
    {"nome": "Faro", "itjobs_id": 9},
    {"nome": "Leiria", "itjobs_id": 13},
    {"nome": "Santarém", "itjobs_id": 20},
    {"nome": "Viseu", "itjobs_id": 16},
    {"nome": "Viana do Castelo", "itjobs_id": 22},
    {"nome": "Vila Real", "itjobs_id": 21},
    {"nome": "Bragança", "itjobs_id": 5},
    {"nome": "Guarda", "itjobs_id": 11},
    {"nome": "Castelo Branco", "itjobs_id": 6},
    {"nome": "Portalegre", "itjobs_id": 12},
    {"nome": "Évora", "itjobs_id": 10},
    {"nome": "Beja", "itjobs_id": 3},
    {"nome": "Madeira", "itjobs_id": 15},
    {"nome": "Açores", "itjobs_id": 2},
    {"nome": "Remoto / Internacional", "itjobs_id": 29},
]

# Nº máximo de vagas devolvidas por fonte, por pesquisa. Aumentado para captar
# o máximo de vagas possível (o site de origem pode demorar mais a responder,
# por isso a interface mostra uma barra de progresso enquanto pesquisa).
MAX_RESULTADOS_POR_FONTE = 80

# User-Agent usado nos pedidos HTTP (identifica-se como um browser normal,
# de forma transparente, sem tentar contornar proteções anti-bot).
USER_AGENT = (
    "Mozilla/5.0 (compatible; PesquisaVagasPT/1.0; "
    "+https://github.com/) AppleWebKit/537.36"
)

REQUEST_TIMEOUT = 10  # segundos
