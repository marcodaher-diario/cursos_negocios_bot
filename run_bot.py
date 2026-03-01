# -*- coding: utf-8 -*-

import os
import re
import feedparser
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.utils import parsedate_to_datetime

# Importando os novos nomes de variáveis do seu configuracoes.py atualizado
from configuracoes import (
    BLOG_ID,
    RSS_FEEDS,
    PALAVRAS_CURSOS_E_CONTEUDO,   # Antiga Policial
    PALAVRAS_NEGOCIOS_DIGITAIS,   # Antiga Politica
    PALAVRAS_OPORTUNIDADES_E_RENDA, # Antiga Economia
    BLOCO_FIXO_FINAL
)

from template_blog import obter_esqueleto_html
from gemini_engine import GeminiEngine
from imagem_engine import ImageEngine


# ==========================================================
# CONFIGURAÇÃO DO NOVO NICHO
# ==========================================================

# Mapeamento: (Dia_da_Semana, "HH:MM") -> Tema
# 0:Seg, 1:Ter, 2:Qua, 3:Qui, 4:Sex, 5:Sab, 6:Dom
AGENDA_POSTAGENS = {
    (1, "15:00"): "cursos",       # Terça
    (3, "15:00"): "cursos",       # Quinta
    (5, "15:00"): "cursos",       # Sábado
    
    (0, "15:00"): "negocios",     # Segunda
    (2, "15:00"): "negocios",     # Quarta
    (4, "15:00"): "negocios",     # Sexta
    
    (0, "17:00"): "oportunidades", # Segunda
    (3, "17:00"): "oportunidades", # Quinta
    (6, "17:00"): "oportunidades", # Domingo
}

def obter_tema_atual():
    agora = obter_horario_brasilia() # Melhor usar sua função de Brasília já pronta
    dia_semana = agora.weekday()
    hora_formatada = agora.strftime("%H:00")
    return AGENDA_POSTAGENS.get((dia_semana, hora_formatada), "tema_padrao")

JANELA_MINUTOS = 60
ARQUIVO_CONTROLE_DIARIO = "controle_diario.txt"
ARQUIVO_POSTS_PUBLICADOS = "posts_publicados.txt"


# ==========================================================
# UTILIDADES E LIMPEZA (NOVA FUNÇÃO ADICIONADA AQUI)
# ==========================================================

def obter_horario_brasilia():
    return datetime.utcnow() - timedelta(hours=3)

def limpar_e_filtrar_conteudo(texto_bruto):
    """Limpa ruídos de feeds externos para manter autoridade."""
    termos_sujos = [
        r"Leia também:.*", r"Confira mais no site.*",
        r"Inscreva-se na nossa newsletter.*", r"Siga-nos nas redes sociais.*",
        r"Assine o clipping.*", r"Conteúdo patrocinado por.*", r"Fonte:.*"
    ]
    texto_limpo = texto_bruto
    for padrao in termos_sujos:
        texto_limpo = re.sub(padrao, "", texto_limpo, flags=re.IGNORECASE)
    # Remove links HTML de terceiros
    texto_limpo = re.sub(r'<a href=".*?">.*?</a>', '', texto_limpo)
    return texto_limpo.strip()

def horario_para_minutos(hhmm):
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m

def dentro_da_janela(min_atual, min_agenda):
    return abs(min_atual - min_agenda) <= JANELA_MINUTOS


# ==========================================================
# CONTROLE DE PUBLICAÇÃO E LINKS (MANTIDOS)
# ==========================================================

def ja_postou(data_str, horario_agenda):
    if not os.path.exists(ARQUIVO_CONTROLE_DIARIO):
        return False
    with open(ARQUIVO_CONTROLE_DIARIO, "r", encoding="utf-8") as f:
        for linha in f:
            linha = linha.strip()
            if not linha or "|" not in linha: continue
            partes = linha.split("|")
            if len(partes) == 2:
                data, hora = partes
                if data == data_str and hora == horario_agenda:
                    return True
    return False

def registrar_postagem(data_str, horario_agenda):
    linhas = []
    if os.path.exists(ARQUIVO_CONTROLE_DIARIO):
        with open(ARQUIVO_CONTROLE_DIARIO, "r", encoding="utf-8") as f:
            linhas = f.readlines()
    nova_linha = f"{data_str}|{horario_agenda}\n"
    if nova_linha not in linhas:
        linhas.append(nova_linha)
    linhas = linhas[-15:]
    with open(ARQUIVO_CONTROLE_DIARIO, "w", encoding="utf-8") as f:
        f.writelines(linhas)

def registrar_link_publicado(link):
    linhas = []
    if os.path.exists(ARQUIVO_POSTS_PUBLICADOS):
        with open(ARQUIVO_POSTS_PUBLICADOS, "r", encoding="utf-8") as f:
            linhas = f.readlines()
    nova_linha = f"{link}\n"
    if nova_linha not in linhas:
        linhas.append(nova_linha)
    linhas = linhas[-100:] 
    with open(ARQUIVO_POSTS_PUBLICADOS, "w", encoding="utf-8") as f:
        f.writelines(linhas)

def link_ja_publicado(link):
    if not os.path.exists(ARQUIVO_POSTS_PUBLICADOS):
        return False
    with open(ARQUIVO_POSTS_PUBLICADOS, "r", encoding="utf-8") as f:
        return any(link.strip() == l.strip() for l in f)


# ==========================================================
# VERIFICAR TEMA (ADAPTADO)
# ==========================================================

def verificar_assunto(titulo, texto):
    conteudo = f"{titulo} {texto}".lower()
    if any(p in conteudo for p in PALAVRAS_CURSOS_E_CONTEUDO):
        return "cursos"
    if any(p in conteudo for p in PALAVRAS_NEGOCIOS_DIGITAIS):
        return "negocios"
    if any(p in conteudo for p in PALAVRAS_OPORTUNIDADES_E_RENDA):
        return "oportunidades"
    return "geral"


# ==========================================================
# GERAR TAGS SEO (MANTIDO)
# ==========================================================

def gerar_tags_seo(titulo, texto):
    stopwords = ["com", "de", "do", "da", "em", "para", "um", "uma", "os", "as", "que", "no", "na", "ao", "aos"]
    conteudo = f"{titulo} {texto[:100]}"
    palavras = re.findall(r'\b\w{4,}\b', conteudo.lower())
    tags = []
    for p in palavras:
        if p not in stopwords and p not in tags:
            tags.append(p.capitalize())
    tags_fixas = ["Negócios", "Cursos", "Empreendedorismo"] # Tags adaptadas
    for tf in tags_fixas:
        if tf not in tags:
            tags.append(tf)
    resultado = []
    tamanho_atual = 0
    for tag in tags:
        if tamanho_atual + len(tag) + 2 <= 200:
            resultado.append(tag)
            tamanho_atual += len(tag) + 2
        else:
            break
    return resultado


# ==========================================================
# BUSCAR NOTÍCIA COM RANKING ESTRATÉGICO (ADAPTADO)
# ==========================================================

def buscar_noticia(tipo):
    pesos_por_tema = {
        "cursos": {
            "curso": 15, "gratuito": 12, "vagas": 10, "e-book": 12, "inscrição": 9,
            "especialização": 10, "treinamento": 9, "mentoria": 11, "certificado": 10
        },
        "negocios": {
            "kiwify": 15, "hotmart": 15, "marketing digital": 13, "afiliado": 12,
            "vendas": 10, "estratégia": 9, "lucro": 10, "eduzz": 12, "copywriting": 11
        },
        "oportunidades": {
            "renda extra": 15, "home office": 12, "trabalho remoto": 12, "mei": 10,
            "franquia": 11, "investimento": 9, "startup": 10, "carreira": 9, "pme": 8
        }
    }

    palavras_peso = pesos_por_tema.get(tipo, {})
    noticias_validas = []
    agora = datetime.utcnow()

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:15]:
            titulo = entry.get("title", "")
            resumo_bruto = entry.get("summary", "")
            link = entry.get("link", "")
            
            # Limpando o resumo antes de qualquer análise
            resumo = limpar_e_filtrar_conteudo(resumo_bruto)

            if not titulo or not link: continue
            if verificar_assunto(titulo, resumo) != tipo: continue
            if link_ja_publicado(link): continue

            # Lógica de imagem original mantida
            imagem = ""
            if "media_content" in entry and len(entry.media_content) > 0:
                imagem = entry.media_content[0].get("url", "")

            # Validação de data original mantida
            data_publicacao = None
            if hasattr(entry, "published"):
                try:
                    data_publicacao = parsedate_to_datetime(entry.published)
                    if data_publicacao.tzinfo is not None:
                        data_publicacao = data_publicacao.astimezone(tz=None).replace(tzinfo=None)
                except: pass

            if data_publicacao:
                if (agora - data_publicacao).days > 1: continue

            conteudo = f"{titulo} {resumo}".lower()
            score = 0
            for palavra, peso in palavras_peso.items():
                if palavra in conteudo: score += peso

            if data_publicacao:
                minutos_passados = (agora - data_publicacao).total_seconds() / 60
                bonus_recencia = max(0, 1000 - minutos_passados) / 1000
                score += bonus_recencia

            noticias_validas.append({
                "titulo": titulo, "texto": resumo, "link": link,
                "imagem": imagem, "score": score
            })

    if not noticias_validas: return None
    noticia_escolhida = max(noticias_validas, key=lambda x: x["score"])
    return noticia_escolhida


# ==========================================================
# MODO TESTE (ADAPTADO PARA NOVOS TEMAS)
# ==========================================================

def executar_modo_teste(tema_forcado=None, publicar=False):
    print("=== MODO TESTE ATIVADO (NICHO NEGÓCIOS) ===")
    if not tema_forcado:
        tema_forcado = "cursos"

    noticia = buscar_noticia(tema_forcado)
    if not noticia:
        print("Nenhuma notícia encontrada para teste.")
        return

    gemini = GeminiEngine()
    imagem_engine = ImageEngine()

    # Passa o resumo já limpo para a IA
    texto_ia = gemini.gerar_analise_jornalistica(noticia["titulo"], noticia["texto"], tema_forcado)
    query_visual = gemini.gerar_query_visual(noticia["titulo"], noticia["texto"])
    imagem_final = imagem_engine.obter_imagem(noticia, tema_forcado, query_ia=query_visual)

    tags = gerar_tags_seo(noticia["titulo"], texto_ia)
    dados = {
        "titulo": noticia["titulo"],
        "imagem": imagem_final,
        "texto_completo": texto_ia,
        "assinatura": BLOCO_FIXO_FINAL
    }

    html = obter_esqueleto_html(dados)
    service = Credentials.from_authorized_user_file("token.json")
    service = build("blogger", "v3", credentials=service)

    service.posts().insert(
        blogId=BLOG_ID,
        body={"title": noticia["titulo"], "content": html, "labels": tags},
        isDraft=not publicar
    ).execute()
    print("Postagem de teste concluída.")


# ==========================================================
# EXECUÇÃO PRINCIPAL (MANTIDA COM ADAPTAÇÃO DE TEMAS)
# ==========================================================

if __name__ == "__main__":
    if os.getenv("TEST_MODE") == "true":
        tema_teste = os.getenv("TEST_TEMA", "cursos")
        publicar_teste = os.getenv("TEST_PUBLICAR", "false") == "true"
        executar_modo_teste(tema_forcado=tema_teste, publicar=publicar_teste)
        exit()

    agora = obter_horario_brasilia()
    dia_atual = agora.weekday() # Pegamos o dia da semana (0-6)
    min_atual = agora.hour * 60 + agora.minute
    data_hoje = agora.strftime("%Y-%m-%d")

    horario_escolhido = None
    tema_escolhido = None

    # Ajustado para desempacotar a tupla ((dia, hora), tema)
    for (dia_agenda, hora_string), tema in AGENDA_POSTAGENS.items():
        if dia_agenda == dia_atual: # Só verifica se for o dia correto
            min_agenda = horario_para_minutos(hora_string)
            if dentro_da_janela(min_atual, min_agenda):
                if not ja_postou(data_hoje, hora_string):
                    horario_escolhido = hora_string
                    tema_escolhido = tema
                    break
    if not horario_escolhido:
        exit()

    noticia = buscar_noticia(tema_escolhido)
    if not noticia:
        exit()

    gemini = GeminiEngine()
    imagem_engine = ImageEngine()

    texto_ia = gemini.gerar_analise_jornalistica(noticia["titulo"], noticia["texto"], tema_escolhido)
    query_visual = gemini.gerar_query_visual(noticia["titulo"], noticia["texto"])
    imagem_final = imagem_engine.obter_imagem(noticia, tema_escolhido, query_ia=query_visual)
    
    tags = gerar_tags_seo(noticia["titulo"], texto_ia)

    dados = {
        "titulo": noticia["titulo"],
        "imagem": imagem_final,
        "texto_completo": texto_ia,
        "assinatura": BLOCO_FIXO_FINAL
    }

    html = obter_esqueleto_html(dados)

    service = Credentials.from_authorized_user_file("token.json")
    service = build("blogger", "v3", credentials=service)

    service.posts().insert(
        blogId=BLOG_ID,
        body={"title": noticia["titulo"], "content": html, "labels": tags},
        isDraft=False
    ).execute()

    registrar_postagem(data_hoje, horario_escolhido)
    registrar_link_publicado(noticia["link"])

    print(f"Post publicado com sucesso: {noticia['titulo']}")
