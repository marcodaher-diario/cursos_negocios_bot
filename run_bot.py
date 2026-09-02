# -*- coding: utf-8 -*-

import os
import re
import random
import feedparser
from zoneinfo import ZoneInfo

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.utils import parsedate_to_datetime
FUSO_BRASILIA = ZoneInfo("America/Sao_Paulo")

# ==========================================================
# IMPORTAÇÕES DAS CONFIGURAÇÕES
# ==========================================================

from configuracoes import (
    BLOG_ID,
    RSS_FEEDS,
    CATEGORIAS_EDITORIAIS,
    TIPOS_DE_CONTEUDO,
    PUBLICOS_ALVO,
    PESOS_POR_TEMA,
    LIMITES_CLUSTER,
    REGRAS_EDITORIAIS,
    BLOCO_FIXO_FINAL,
    MIN_PALAVRAS,
    MAX_PALAVRAS
)

from template_blog import obter_esqueleto_html
from gemini_engine import GeminiEngine
from imagem_engine import ImageEngine


# ==========================================================
# CONFIGURAÇÃO DE FUSO
# ==========================================================

FUSO_BRASILIA = ZoneInfo("America/Sao_Paulo")


# ==========================================================
# AGENDA DE PUBLICAÇÃO
# ==========================================================
#
# 0 = Segunda
# 1 = Terça
# 2 = Quarta
# 3 = Quinta
# 4 = Sexta
# 5 = Sábado
# 6 = Domingo
#
# A agenda abaixo mantém a lógica anterior:
#
# Terça, Quinta e Sábado = cursos
# Segunda, Quarta e Sexta = negócios
# Segunda, Quinta e Domingo = oportunidades
#
# Porém, agora o conceito de "tema" é convertido em
# categorias/clusters da nova configuração.
#
# ==========================================================

AGENDA_POSTAGENS = {
    (1, "15:00"): "cursos e capacitação",
    (3, "15:00"): "cursos e capacitação",
    (5, "15:00"): "cursos e capacitação",

    (0, "15:00"): "negócios digitais",
    (2, "15:00"): "negócios digitais",
    (4, "15:00"): "negócios digitais",

    (0, "17:00"): "renda extra",
    (3, "17:00"): "renda extra",
    (6, "17:00"): "renda extra",
}


# ==========================================================
# CONFIGURAÇÃO DE JANELA
# ==========================================================

try:
    JANELA_MINUTOS = int(
        os.getenv("JANELA_POSTAGEM_MINUTOS", "90")
    )
except ValueError:
    JANELA_MINUTOS = 90


# ==========================================================
# ARQUIVOS DE CONTROLE
# ==========================================================

ARQUIVO_CONTROLE_DIARIO = "controle_diario.txt"

ARQUIVO_POSTS_PUBLICADOS = "posts_publicados.txt"

ARQUIVO_CONTROLE_TEMAS = "controle_temas_usados.txt"


# ==========================================================
# UTILIDADES DE DATA E HORA
# ==========================================================

def obter_horario_brasilia():
    return datetime.now(FUSO_BRASILIA)


def horario_para_minutos(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m


def diferenca_circular_minutos(min_atual, min_agenda):
    diferenca = abs(min_atual - min_agenda)
    return min(diferenca, 1440 - diferenca)


def dentro_da_janela(min_atual, min_agenda):
    return (
        diferenca_circular_minutos(
            min_atual,
            min_agenda
        ) <= JANELA_MINUTOS
    )


# ==========================================================
# LIMPEZA DE CONTEÚDO RSS
# ==========================================================

def limpar_e_filtrar_conteudo(texto_bruto):

    if not texto_bruto:
        return ""

    termos_sujos = [
        r"Leia também:.*",
        r"Confira mais no site.*",
        r"Inscreva-se na nossa newsletter.*",
        r"Siga-nos nas redes sociais.*",
        r"Assine o clipping.*",
        r"Conteúdo patrocinado por.*",
        r"Fonte:.*"
    ]

    texto_limpo = texto_bruto

    for padrao in termos_sujos:
        texto_limpo = re.sub(
            padrao,
            "",
            texto_limpo,
            flags=re.IGNORECASE | re.DOTALL
        )

    # Remove links HTML
    texto_limpo = re.sub(
        r'<a\s+href=".*?">.*?</a>',
        '',
        texto_limpo,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Remove outras tags HTML
    texto_limpo = re.sub(
        r"<[^>]+>",
        " ",
        texto_limpo
    )

    texto_limpo = re.sub(
        r"\s+",
        " ",
        texto_limpo
    )

    return texto_limpo.strip()


# ==========================================================
# NORMALIZAÇÃO
# ==========================================================

def normalizar_texto(texto):

    if not texto:
        return ""

    texto = texto.lower()

    # Remove acentos para comparação
    substituicoes = {
        "á": "a",
        "à": "a",
        "ã": "a",
        "â": "a",
        "ä": "a",
        "é": "e",
        "è": "e",
        "ê": "e",
        "ë": "e",
        "í": "i",
        "ì": "i",
        "î": "i",
        "ï": "i",
        "ó": "o",
        "ò": "o",
        "õ": "o",
        "ô": "o",
        "ö": "o",
        "ú": "u",
        "ù": "u",
        "û": "u",
        "ü": "u",
        "ç": "c"
    }

    for original, substituto in substituicoes.items():
        texto = texto.replace(original, substituto)

    texto = re.sub(r"\s+", " ", texto)

    return texto.strip()


# ==========================================================
# CONTROLE DE PUBLICAÇÃO
# ==========================================================

def ja_postou(data_str, horario_agenda):

    if not os.path.exists(ARQUIVO_CONTROLE_DIARIO):
        return False

    with open(
        ARQUIVO_CONTROLE_DIARIO,
        "r",
        encoding="utf-8"
    ) as f:

        for linha in f:

            linha = linha.strip()

            if not linha or "|" not in linha:
                continue

            partes = linha.split("|", 1)

            if len(partes) != 2:
                continue

            data, hora = partes

            if (
                data == data_str
                and hora == horario_agenda
            ):
                return True

    return False


def registrar_postagem(data_str, horario_agenda):

    linhas = []

    if os.path.exists(ARQUIVO_CONTROLE_DIARIO):

        with open(
            ARQUIVO_CONTROLE_DIARIO,
            "r",
            encoding="utf-8"
        ) as f:

            linhas = f.readlines()

    nova_linha = f"{data_str}|{horario_agenda}\n"

    if nova_linha not in linhas:
        linhas.append(nova_linha)

    # Mantém apenas os últimos registros
    linhas = linhas[-30:]

    with open(
        ARQUIVO_CONTROLE_DIARIO,
        "w",
        encoding="utf-8"
    ) as f:

        f.writelines(linhas)


# ==========================================================
# CONTROLE DE LINKS
# ==========================================================

def registrar_link_publicado(link):

    if not link:
        return

    linhas = []

    if os.path.exists(ARQUIVO_POSTS_PUBLICADOS):

        with open(
            ARQUIVO_POSTS_PUBLICADOS,
            "r",
            encoding="utf-8"
        ) as f:

            linhas = f.readlines()

    nova_linha = f"{link}\n"

    if nova_linha not in linhas:
        linhas.append(nova_linha)

    linhas = linhas[-100:]

    with open(
        ARQUIVO_POSTS_PUBLICADOS,
        "w",
        encoding="utf-8"
    ) as f:

        f.writelines(linhas)


def link_ja_publicado(link):

    if not link:
        return False

    if not os.path.exists(ARQUIVO_POSTS_PUBLICADOS):
        return False

    with open(
        ARQUIVO_POSTS_PUBLICADOS,
        "r",
        encoding="utf-8"
    ) as f:

        return any(
            link.strip() == linha.strip()
            for linha in f
        )


# ==========================================================
# CONTROLE DE TEMAS
# ==========================================================

def tema_ja_utilizado(titulo, dias=20):

    if not os.path.exists(ARQUIVO_CONTROLE_TEMAS):
        return False

    titulo_normalizado = normalizar_texto(titulo)

    agora = obter_horario_brasilia()

    with open(
        ARQUIVO_CONTROLE_TEMAS,
        "r",
        encoding="utf-8"
    ) as f:

        for linha in f:

            linha = linha.strip()

            if "|" not in linha:
                continue

            partes = linha.split("|", 1)

            if len(partes) != 2:
                continue

            data_str, titulo_salvo = partes

            try:

                data_tema = datetime.strptime(
                    data_str,
                    "%Y-%m-%d"
                ).replace(
                    tzinfo=FUSO_BRASILIA
                )

            except ValueError:
                continue

            diferenca = (
                agora - data_tema
            ).days

            if diferenca >= dias:
                continue

            if (
                normalizar_texto(titulo_salvo)
                == titulo_normalizado
            ):
                return True

    return False


def registrar_tema(titulo):

    hoje = obter_horario_brasilia().strftime(
        "%Y-%m-%d"
    )

    with open(
        ARQUIVO_CONTROLE_TEMAS,
        "a",
        encoding="utf-8"
    ) as f:

        f.write(
            f"{hoje}|{titulo}\n"
        )


# ==========================================================
# CLASSIFICAÇÃO DE ASSUNTO
# ==========================================================

def obter_palavras_do_cluster(categoria):

    categoria_normalizada = normalizar_texto(
        categoria
    )

    mapa = {

        "cursos e capacitacao": [
            "curso",
            "cursos",
            "capacitacao",
            "qualificacao",
            "certificado",
            "certificacao",
            "especializacao",
            "treinamento",
            "mentoria",
            "e-book",
            "ebook",
            "bolsa de estudos",
            "curso gratuito",
            "curso online",
            "profissao",
            "carreira"
        ],

        "profissoes e carreira": [
            "profissao",
            "profissoes",
            "carreira",
            "emprego",
            "vaga",
            "recolocacao",
            "qualificacao",
            "curriculo",
            "entrevista",
            "linkedin"
        ],

        "trabalho remoto": [
            "trabalho remoto",
            "home office",
            "trabalho em casa",
            "vaga remota",
            "emprego remoto",
            "freelancer"
        ],

        "renda extra": [
            "renda extra",
            "ganhar dinheiro",
            "dinheiro extra",
            "segunda renda",
            "renda complementar",
            "trabalho extra",
            "afiliado",
            "freelancer"
        ],

        "empreendedorismo": [
            "empreendedorismo",
            "empreendedor",
            "abrir negocio",
            "negocio proprio",
            "pequeno negocio",
            "pme",
            "mei",
            "franquia",
            "startup"
        ],

        "negocios digitais": [
            "marketing digital",
            "negocio digital",
            "negocios digitais",
            "afiliado",
            "vendas online",
            "infoproduto",
            "hotmart",
            "kiwify",
            "eduzz",
            "copywriting",
            "trafego pago",
            "seo"
        ],

        "marketing digital": [
            "marketing digital",
            "marketing de conteudo",
            "copywriting",
            "trafego pago",
            "trafego organico",
            "seo",
            "branding",
            "funil de vendas",
            "landing page"
        ],

        "programas de afiliados": [
            "afiliado",
            "afiliados",
            "programa de afiliados",
            "marketing de afiliados",
            "hotmart",
            "kiwify",
            "eduzz",
            "monetizze",
            "braip"
        ],

        "infoprodutos e produtos digitais": [
            "infoproduto",
            "produto digital",
            "e-book",
            "ebook",
            "curso online",
            "mentoria"
        ],

        "e-commerce": [
            "e-commerce",
            "ecommerce",
            "loja virtual",
            "loja online",
            "marketplace",
            "mercado livre",
            "shopee",
            "amazon",
            "shopify",
            "nuvemshop",
            "dropshipping"
        ],

        "vendas online": [
            "vendas online",
            "vender online",
            "vender pela internet",
            "loja virtual",
            "marketplace",
            "checkout",
            "conversao"
        ],

        "inteligencia artificial": [
            "inteligencia artificial",
            "ia generativa",
            "chatgpt",
            "gemini",
            "claude",
            "copilot",
            "ferramentas de ia",
            "automacao com ia",
            "ia para negocios"
        ],

        "produtividade": [
            "produtividade",
            "organizacao",
            "gestao do tempo",
            "automacao",
            "ferramentas",
            "eficiencia"
        ],

        "gestao de negocios": [
            "gestao de negocios",
            "gestao empresarial",
            "gestao financeira",
            "gestao de clientes",
            "gestao de vendas",
            "planejamento empresarial",
            "produtividade"
        ],

        "financas para empreendedores": [
            "fluxo de caixa",
            "capital de giro",
            "lucro",
            "faturamento",
            "precificacao",
            "margem de lucro",
            "custos",
            "despesas",
            "controle financeiro",
            "roi"
        ],

        "mei e pequenos negocios": [
            "mei",
            "microempreendedor",
            "pequeno negocio",
            "pme",
            "cnpj",
            "nota fiscal",
            "formalizacao"
        ],

        "franquias e oportunidades": [
            "franquia",
            "franquias",
            "microfranquia",
            "oportunidade",
            "negocio proprio"
        ],

        "startups e inovacao": [
            "startup",
            "startups",
            "inovacao",
            "tecnologia",
            "investimento",
            "escalabilidade"
        ]
    }

    return mapa.get(
        categoria_normalizada,
        []
    )


def verificar_assunto(titulo, texto):

    conteudo = normalizar_texto(
        f"{titulo} {texto}"
    )

    pontuacoes = []

    for categoria in CATEGORIAS_EDITORIAIS:

        palavras = obter_palavras_do_cluster(
            categoria
        )

        pontos = 0

        for palavra in palavras:

            palavra_normalizada = normalizar_texto(
                palavra
            )

            if palavra_normalizada in conteudo:
                pontos += 1

        if pontos > 0:

            pontuacoes.append(
                (pontos, categoria)
            )

    if not pontuacoes:
        return "geral"

    pontuacoes.sort(
        key=lambda x: x[0],
        reverse=True
    )

    return pontuacoes[0][1]


# ==========================================================
# GERAR TAGS SEO
# ==========================================================

def gerar_tags_seo(titulo, texto):

    stopwords = {
        "com", "de", "do", "da", "dos", "das",
        "em", "para", "por", "um", "uma",
        "uns", "umas", "os", "as",
        "que", "no", "na", "nos", "nas",
        "ao", "aos", "e", "ou",
        "como", "mais", "sobre"
    }

    conteudo = (
        f"{titulo} {texto[:5000]}"
    )

    tags = []

    def adicionar_tag(tag):

        if not tag:
            return

        tag = tag.strip()

        if len(tag) < 3:
            return

        existentes = {
            normalizar_texto(t)
            for t in tags
        }

        if normalizar_texto(tag) not in existentes:
            tags.append(tag)

    # ------------------------------------------------------
    # Categorias
    # ------------------------------------------------------

    for categoria in CATEGORIAS_EDITORIAIS:

        palavras = obter_palavras_do_cluster(
            categoria
        )

        conteudo_normalizado = normalizar_texto(
            conteudo
        )

        for palavra in palavras:

            if normalizar_texto(palavra) in conteudo_normalizado:

                adicionar_tag(palavra)

    # ------------------------------------------------------
    # Palavras do título
    # ------------------------------------------------------

    palavras_titulo = re.findall(
        r"\b[\wÀ-ÿ-]{4,}\b",
        titulo.lower()
    )

    for palavra in palavras_titulo:

        if palavra in stopwords:
            continue

        adicionar_tag(
            palavra.capitalize()
        )

    # ------------------------------------------------------
    # Combinações de palavras do título
    # ------------------------------------------------------

    palavras_limpa = [
        p for p in palavras_titulo
        if p not in stopwords
    ]

    for i in range(
        len(palavras_limpa) - 1
    ):

        bigrama = (
            palavras_limpa[i]
            + " "
            + palavras_limpa[i + 1]
        )

        adicionar_tag(
            bigrama.capitalize()
        )

    # ------------------------------------------------------
    # Tags fixas
    # ------------------------------------------------------

    tags_fixas = [
        "Negócios",
        "Empreendedorismo",
        "Cursos",
        "Renda Extra",
        "Carreira",
        "Marketing Digital"
    ]

    for tag in tags_fixas:
        adicionar_tag(tag)

    # ------------------------------------------------------
    # Limite Blogger
    # ------------------------------------------------------

    resultado = []

    tamanho_atual = 0

    for tag in tags:

        incremento = (
            len(tag) + 2
        )

        if (
            tamanho_atual
            + incremento
            <= 200
        ):

            resultado.append(tag)

            tamanho_atual += incremento

        if len(resultado) >= 15:
            break

    return resultado


# ==========================================================
# BUSCAR NOTÍCIAS COM RANKING
# ==========================================================

def buscar_noticia(categoria):

    noticias_validas = []

    agora = datetime.now(FUSO_BRASILIA)

    categoria_normalizada = normalizar_texto(
        categoria
    )

    # Obtém pesos relacionados ao cluster
    tipo_peso = None

    mapa_pesos = {
        "cursos e capacitacao": "cursos",
        "renda extra": "renda_extra",
        "negocios digitais": "negocios_digitais",
        "empreendedorismo": "empreendedorismo",
        "profissoes e carreira": "carreira",
        "trabalho remoto": "carreira",
        "e-commerce": "ecommerce",
        "vendas online": "ecommerce",
        "inteligencia artificial": "inteligencia_artificial",
        "financas para empreendedores": "financas"
    }

    tipo_peso = mapa_pesos.get(
        categoria_normalizada
    )

    palavras_peso = PESOS_POR_TEMA.get(
        tipo_peso,
        {}
    )

    for feed_url in RSS_FEEDS:

        try:

            feed = feedparser.parse(
                feed_url
            )

        except Exception as e:

            print(
                f"Erro ao ler RSS: {feed_url}"
            )
            print(e)
            continue

        for entry in feed.entries[:20]:

            titulo = entry.get(
                "title",
                ""
            )

            resumo_bruto = entry.get(
                "summary",
                ""
            )

            link = entry.get(
                "link",
                ""
            )

            resumo = limpar_e_filtrar_conteudo(
                resumo_bruto
            )

            if not titulo or not link:
                continue

            if link_ja_publicado(link):
                continue

            categoria_detectada = verificar_assunto(
                titulo,
                resumo
            )

            # Se a notícia tiver classificação,
            # priorizamos o cluster solicitado.
            if (
                categoria_detectada != categoria
                and categoria_detectada != "geral"
            ):
                palavras_categoria = (
                    obter_palavras_do_cluster(
                        categoria
                    )
                )

                conteudo_normalizado = normalizar_texto(
                    f"{titulo} {resumo}"
                )

                encontrou_relacao = any(
                    normalizar_texto(p)
                    in conteudo_normalizado
                    for p in palavras_categoria
                )

                if not encontrou_relacao:
                    continue

            # ------------------------------------------------
            # IMAGEM DO FEED
            # ------------------------------------------------

            imagem = ""

            if (
                "media_content" in entry
                and len(entry.media_content) > 0
            ):

                imagem = entry.media_content[0].get(
                    "url",
                    ""
                )

            # ------------------------------------------------
            # DATA
            # ------------------------------------------------

            data_publicacao = None

            if hasattr(entry, "published"):

                try:

                    data_publicacao = (
                        parsedate_to_datetime(
                            entry.published
                        )
                    )

                    data_publicacao = (
                        data_publicacao
                        .astimezone(
                            ZoneInfo(
                                "America/Sao_Paulo"
                            )
                        )
                        .replace(tzinfo=None)
                    )

                except Exception:
                    data_publicacao = None

            # ------------------------------------------------
            # DESCARTA NOTÍCIAS MUITO ANTIGAS
            # ------------------------------------------------

            if data_publicacao:

                diferenca_horas = (
                    datetime.now()
                    - data_publicacao
                ).total_seconds() / 3600

                if diferenca_horas > 48:
                    continue

            # ------------------------------------------------
            # RANKING
            # ------------------------------------------------

            conteudo = normalizar_texto(
                f"{titulo} {resumo}"
            )

            score = 0

            # Peso das palavras estratégicas
            for palavra, peso in palavras_peso.items():

                if (
                    normalizar_texto(palavra)
                    in conteudo
                ):

                    score += peso

            # Bônus para palavras do cluster
            palavras_cluster = (
                obter_palavras_do_cluster(
                    categoria
                )
            )

            for palavra in palavras_cluster:

                if (
                    normalizar_texto(palavra)
                    in conteudo
                ):

                    score += 3

            # Bônus de recência
            if data_publicacao:

                minutos_passados = (
                    datetime.now()
                    - data_publicacao
                ).total_seconds() / 60

                bonus_recencia = max(
                    0,
                    1000 - minutos_passados
                ) / 1000

                score += bonus_recencia

            # Pequena aleatoriedade para impedir
            # que sempre seja escolhida exatamente
            # a mesma notícia quando os scores
            # são próximos.
            score += random.uniform(
                0,
                0.5
            )

            noticias_validas.append({

                "titulo": titulo,

                "texto": resumo,

                "link": link,

                "imagem": imagem,

                "score": score

            })

    if not noticias_validas:
        return None

    noticias_validas.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    # Mostra no log as melhores opções
    print("\nMelhores notícias encontradas:")

    for noticia in noticias_validas[:5]:

        print(
            f"  Score {noticia['score']:.2f} - "
            f"{noticia['titulo']}"
        )

    return noticias_validas[0]


# ==========================================================
# GERAR BRIEFING PARA O GEMINI
# ==========================================================

def criar_briefing_editorial(
    categoria,
    noticia
):

    tipo_conteudo = random.choice(
        TIPOS_DE_CONTEUDO
    )

    publico = random.choice(
        PUBLICOS_ALVO
    )

    regras = "\n".join(
        f"- {regra}"
        for regra in REGRAS_EDITORIAIS
    )

    briefing = f"""
CATEGORIA PRINCIPAL:
{categoria}

TIPO DE CONTEÚDO:
{tipo_conteudo}

PÚBLICO-ALVO:
{publico}

TÍTULO DA NOTÍCIA/FONTE:
{noticia['titulo']}

RESUMO DA FONTE:
{noticia['texto']}

OBJETIVO:
Transformar o assunto da fonte em um artigo original,
útil, informativo e relevante para o público brasileiro.

O artigo NÃO deve simplesmente copiar ou reescrever
a notícia original.

Deve explicar o assunto com contexto, exemplos,
informações práticas e linguagem natural.

REGRAS EDITORIAIS:
{regras}

TAMANHO:
Entre {MIN_PALAVRAS} e {MAX_PALAVRAS} palavras.

IMPORTANTE:
Não invente dados, números, estatísticas, pesquisas,
empresas, leis ou declarações que não possam ser
sustentados pelo contexto fornecido.

Não prometa ganhos financeiros garantidos.

Não trate renda extra como dinheiro fácil.

Evite clickbait enganoso.

Crie um conteúdo que realmente ajude o leitor.
"""

    return briefing, tipo_conteudo, publico


# ==========================================================
# MODO TESTE
# ==========================================================

def executar_modo_teste(
    tema_forcado=None,
    publicar=False
):

    print(
        "=== MODO TESTE ATIVADO "
        "(NICHO NEGÓCIOS) ==="
    )

    if not tema_forcado:
        tema_forcado = "cursos e capacitação"

    # ------------------------------------------------------
    # Se TEST_TEMA for um cluster antigo,
    # converte para a nova estrutura.
    # ------------------------------------------------------

    equivalencias = {

        "cursos":
            "cursos e capacitação",

        "negocios":
            "negócios digitais",

        "oportunidades":
            "renda extra"
    }

    tema_forcado = equivalencias.get(
        normalizar_texto(tema_forcado),
        tema_forcado
    )

    print(
        f"Categoria de teste: {tema_forcado}"
    )

    noticia = buscar_noticia(
        tema_forcado
    )

    if not noticia:

        print(
            "Nenhuma notícia encontrada para teste."
        )

        return

    gemini = GeminiEngine()

    imagem_engine = ImageEngine()

    briefing, tipo_conteudo, publico = (
        criar_briefing_editorial(
            tema_forcado,
            noticia
        )
    )

    print(
        f"Tipo de conteúdo: {tipo_conteudo}"
    )

    print(
        f"Público: {publico}"
    )

    # ------------------------------------------------------
    # GERA ARTIGO
    # ------------------------------------------------------

    texto_ia = (
        gemini.gerar_analise_jornalistica(
            noticia["titulo"],
            briefing,
            tema_forcado
        )
    )

    if not texto_ia:

        print(
            "Gemini não retornou conteúdo."
        )

        return

    # ------------------------------------------------------
    # GERA QUERY DA IMAGEM
    # ------------------------------------------------------

    query_visual = (
        gemini.gerar_query_visual(
            noticia["titulo"],
            noticia["texto"]
        )
    )

    imagem_final = (
        imagem_engine.obter_imagem(
            noticia,
            tema_forcado,
            query_ia=query_visual
        )
    )

    # ------------------------------------------------------
    # TAGS
    # ------------------------------------------------------

    tags_geradas = gerar_tags_seo(
        noticia["titulo"],
        texto_ia
    )

    tags_finais = [
        str(t).strip()
        for t in tags_geradas
        if t
    ]

    if not tags_finais:

        tags_finais = [
            "Negócios",
            "Empreendedorismo"
        ]

    # ------------------------------------------------------
    # HTML
    # ------------------------------------------------------

    dados = {

        "titulo":
            noticia["titulo"],

        "imagem":
            imagem_final,

        "texto_completo":
            texto_ia,

        "assinatura":
            BLOCO_FIXO_FINAL
    }

    html = obter_esqueleto_html(
        dados
    )

    # ------------------------------------------------------
    # BLOGGER
    # ------------------------------------------------------

    try:

        creds = (
            Credentials
            .from_authorized_user_file(
                "token.json"
            )
        )

        service = build(
            "blogger",
            "v3",
            credentials=creds
        )

        service.posts().insert(

            blogId=BLOG_ID,

            body={

                "title":
                    noticia["titulo"],

                "content":
                    html,

                "labels":
                    tags_finais
            },

            isDraft=not publicar

        ).execute()

        print(
            f"✅ Sucesso total: "
            f"{noticia['titulo']}"
        )

        print(
            f"Tags: {tags_finais}"
        )

        if publicar:

            registrar_link_publicado(
                noticia["link"]
            )

    except Exception as e:

        print(
            f"❌ Erro no Blogger: {e}"
        )

        print(
            f"DEBUG - Tags tentadas: "
            f"{tags_finais}"
        )


# ==========================================================
# EXECUÇÃO PRINCIPAL
# ==========================================================

if __name__ == "__main__":

    # ======================================================
    # MODO TESTE
    # ======================================================

    if os.getenv("TEST_MODE") == "true":

        tema_teste = os.getenv(
            "TEST_TEMA",
            "cursos e capacitação"
        )

        publicar_teste = (
            os.getenv(
                "TEST_PUBLICAR",
                "false"
            ).lower()
            == "true"
        )

        executar_modo_teste(
            tema_forcado=tema_teste,
            publicar=publicar_teste
        )

        raise SystemExit


    # ======================================================
    # HORÁRIO ATUAL
    # ======================================================

    agora = obter_horario_brasilia()

    dia_atual = agora.weekday()

    min_atual = (
        agora.hour * 60
        + agora.minute
    )

    data_hoje = agora.strftime(
        "%Y-%m-%d"
    )


    # ======================================================
    # VERIFICA AGENDA
    # ======================================================

    horario_escolhido = None

    categoria_escolhida = None

    candidatos = []

    for (
        dia_agenda,
        hora_string
    ), categoria in AGENDA_POSTAGENS.items():

        if dia_agenda != dia_atual:
            continue

        try:

            min_agenda = (
                horario_para_minutos(
                    hora_string
                )
            )

        except ValueError:

            print(
                f"Horário inválido: "
                f"{hora_string}"
            )

            continue

        distancia = (
            diferenca_circular_minutos(
                min_atual,
                min_agenda
            )
        )

        if distancia <= JANELA_MINUTOS:

            if not ja_postou(
                data_hoje,
                hora_string
            ):

                candidatos.append(
                    (
                        distancia,
                        hora_string,
                        categoria
                    )
                )


    # ======================================================
    # SE EXISTIR MAIS DE UM HORÁRIO POSSÍVEL,
    # ESCOLHE O MAIS PRÓXIMO
    # ======================================================

    if candidatos:

        candidatos.sort(
            key=lambda x: x[0]
        )

        (
            distancia,
            horario_escolhido,
            categoria_escolhida
        ) = candidatos[0]


    # ======================================================
    # RECUPERAÇÃO DE PUBLICAÇÃO ATRASADA
    # ======================================================
    #
    # Se o GitHub Actions executar muito depois
    # do horário original, procura uma publicação
    # daquele mesmo dia que ainda não foi registrada.
    #
    # Exemplo:
    # Agenda = 15:00
    # Execução = 23:42
    #
    # A publicação atrasada pode ser recuperada.
    #
    # ======================================================

    if not horario_escolhido:

        horarios_atrasados = []

        for (
            dia_agenda,
            hora_string
        ), categoria in AGENDA_POSTAGENS.items():

            if dia_agenda != dia_atual:
                continue

            try:

                min_agenda = (
                    horario_para_minutos(
                        hora_string
                    )
                )

            except ValueError:

                continue

            # Somente horários que já passaram
            if min_agenda < min_atual:

                if not ja_postou(
                    data_hoje,
                    hora_string
                ):

                    atraso = (
                        min_atual
                        - min_agenda
                    )

                    horarios_atrasados.append(
                        (
                            atraso,
                            hora_string,
                            categoria
                        )
                    )

        if horarios_atrasados:

            horarios_atrasados.sort(
                key=lambda x: x[0]
            )

            (
                atraso,
                horario_escolhido,
                categoria_escolhida
            ) = horarios_atrasados[0]

            print(
                "\n"
                + "=" * 60
            )

            print(
                ">>> PUBLICAÇÃO ATRASADA DETECTADA <<<"
            )

            print(
                f"Horário original: "
                f"{horario_escolhido}"
            )

            print(
                f"Horário atual: "
                f"{agora.strftime('%H:%M')}"
            )

            print(
                "A publicação será recuperada agora."
            )

            print(
                "=" * 60
            )


    # ======================================================
    # FORÇAR POSTAGEM
    # ======================================================

    if not horario_escolhido:

        if (
            os.getenv(
                "FORCAR_POSTAGEM",
                "false"
            ).lower()
            == "true"
        ):

            horario_escolhido = (
                f"FORCADO-"
                f"{agora.strftime('%H:%M')}"
            )

            categoria_escolhida = random.choice(
                CATEGORIAS_EDITORIAIS
            )

            print(
                "FORÇAR POSTAGEM ativado."
            )

            print(
                f"Categoria escolhida: "
                f"{categoria_escolhida}"
            )

        else:

            print(
                "Fora da janela de postagem."
            )

            print(
                f"Horário atual: "
                f"{agora.strftime('%H:%M')}"
            )

            print(
                f"Janela utilizada: "
                f"{JANELA_MINUTOS} minutos"
            )

            print(
                "Nenhuma ação realizada."
            )

            raise SystemExit


    # ======================================================
    # INFORMAÇÕES DA EXECUÇÃO
    # ======================================================

    print(
        "\n"
        + "=" * 60
    )

    print(
        "BOT BLOGGER — NEGÓCIOS E OPORTUNIDADES"
    )

    print(
        "=" * 60
    )

    print(
        f"Data/hora Brasília: "
        f"{agora.strftime('%d/%m/%Y %H:%M:%S')}"
    )

    print(
        f"Horário selecionado: "
        f"{horario_escolhido}"
    )

    print(
        f"Categoria: "
        f"{categoria_escolhida}"
    )

    print(
        f"Janela: "
        f"{JANELA_MINUTOS} minutos"
    )

    print(
        "=" * 60
    )


    # ======================================================
    # BUSCAR NOTÍCIA
    # ======================================================

    print(
        "\nBuscando notícia relevante..."
    )

    noticia = buscar_noticia(
        categoria_escolhida
    )

    if not noticia:

        print(
            "Nenhuma notícia adequada encontrada."
        )

        raise SystemExit


    print(
        "\n"
        + "=" * 60
    )

    print(
        "NOTÍCIA SELECIONADA"
    )

    print(
        "=" * 60
    )

    print(
        f"Título: "
        f"{noticia['titulo']}"
    )

    print(
        f"Score: "
        f"{noticia['score']:.2f}"
    )

    print(
        f"Link: "
        f"{noticia['link']}"
    )

    print(
        "=" * 60
    )


    # ======================================================
    # GEMINI + IMAGEM
    # ======================================================

    print(
        "\n"
        + "=" * 60
    )

    print(
        "GERANDO CONTEÚDO"
    )

    print(
        "=" * 60
    )

    gemini = GeminiEngine()

    imagem_engine = ImageEngine()


    # ======================================================
    # BRIEFING EDITORIAL
    # ======================================================

    briefing, tipo_conteudo, publico = (
        criar_briefing_editorial(
            categoria_escolhida,
            noticia
        )
    )

    print(
        f"Tipo de conteúdo: "
        f"{tipo_conteudo}"
    )

    print(
        f"Público-alvo: "
        f"{publico}"
    )


    # ======================================================
    # GERAR ARTIGO
    # ======================================================

    print(
        "Gerando artigo com Gemini..."
    )

    texto_ia = (
        gemini.gerar_analise_jornalistica(
            noticia["titulo"],
            briefing,
            categoria_escolhida
        )
    )

    if not texto_ia:

        print(
            "ERRO: Gemini não retornou artigo."
        )

        raise SystemExit


    # ======================================================
    # GERAR QUERY VISUAL
    # ======================================================

    print(
        "Gerando consulta para imagem..."
    )

    query_visual = (
        gemini.gerar_query_visual(
            noticia["titulo"],
            noticia["texto"]
        )
    )


    # ======================================================
    # BUSCAR IMAGEM
    # ======================================================

    print(
        "Obtendo imagem..."
    )

    imagem_final = (
        imagem_engine.obter_imagem(
            noticia,
            categoria_escolhida,
            query_ia=query_visual
        )
    )


    # ======================================================
    # TAGS SEO
    # ======================================================

    print(
        "Gerando tags SEO..."
    )

    tags = gerar_tags_seo(
        noticia["titulo"],
        texto_ia
    )

    print(
        f"Tags: {tags}"
    )


    # ======================================================
    # MONTAR HTML
    # ======================================================

    dados = {

        "titulo":
            noticia["titulo"],

        "imagem":
            imagem_final,

        "texto_completo":
            texto_ia,

        "assinatura":
            BLOCO_FIXO_FINAL
    }

    html = obter_esqueleto_html(
        dados
    )


    # ======================================================
    # AUTENTICAÇÃO BLOGGER
    # ======================================================

    print(
        "Autenticando no Blogger..."
    )

    creds = (
        Credentials
        .from_authorized_user_file(
            "token.json"
        )
    )

    service = build(
        "blogger",
        "v3",
        credentials=creds
    )


    # ======================================================
    # PUBLICAÇÃO
    # ======================================================

    print(
        "Publicando artigo..."
    )

    service.posts().insert(

        blogId=BLOG_ID,

        body={

            "title":
                noticia["titulo"],

            "content":
                html,

            "labels":
                tags
        },

        isDraft=False

    ).execute()


    # ======================================================
    # REGISTRAR CONTROLES
    # ======================================================

    registrar_postagem(
        data_hoje,
        horario_escolhido
    )

    registrar_link_publicado(
        noticia["link"]
    )

    registrar_tema(
        noticia["titulo"]
    )


    # ======================================================
    # FINAL
    # ======================================================

    print(
        "\n"
        + "=" * 60
    )

    print(
        "✅ POST PUBLICADO COM SUCESSO!"
    )

    print(
        f"Título: {noticia['titulo']}"
    )

    print(
        f"Categoria: {categoria_escolhida}"
    )

    print(
        f"Tipo: {tipo_conteudo}"
    )

    print(
        f"Público: {publico}"
    )

    print(
        "=" * 60
    )
