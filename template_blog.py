# -*- coding: utf-8 -*-
import re

# ==========================================================
# CONFIGURAÇÃO DE IDENTIDADE VISUAL (O SEGREDO DO CORINGA)
# ==========================================================
# Altere estes valores para mudar o visual de qualquer blog instantaneamente
CONFIG_VISUAL = {
    "cor_primaria": "rgb(7, 55, 99)",  # Azul escuro (seu padrão MD)
    "fonte_principal": "Arial, sans-serif",
    "tamanho_titulo": "28px",
    "tamanho_subtitulo": "20px",
    "tamanho_corpo": "18px",
    "max_width": "900px"
}

def formatar_texto_ultra(texto_bruto, titulo_principal):
    if not texto_bruto:
        return ""

    linhas = [l.strip() for l in texto_bruto.split("\n") if l.strip()]
    html_final = ""
    titulo_norm = titulo_principal.strip().lower()
    
    em_lista = False

    for linha in linhas:
        # 1. PROCESSAMENTO DE MARKDOWN
        # Negrito: **texto** -> <strong>
        linha = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", linha)
        # Itálico: *texto* ou _texto_ -> <em> (Evitando conflito com listas)
        linha = re.sub(r"(?<!\*)\*(?!\*)(.*?)\*", r"<em>\1</em>", linha)
        
        # 2. IDENTIFICAÇÃO DE LISTAS (Inicia com * ou - ou •)
        match_lista = re.match(r"^[\*\-\•]\s*(.*)", linha)
        if match_lista:
            conteudo_item = match_lista.group(1)
            if not em_lista:
                html_final += '<ul class="lista-blog">\n'
                em_lista = True
            html_final += f'  <li>{conteudo_item}</li>\n'
            continue
        else:
            if em_lista:
                html_final += '</ul>\n'
                em_lista = False

        # 3. LIMPEZA DE MARCADORES RESTANTES (# das pontas)
        linha_limpa = linha.lstrip("# ").strip()

        # 4. FILTRO DE REPETIÇÃO DO TÍTULO
        if linha_limpa.lower() == titulo_norm:
            continue
        
        if not linha_limpa:
            continue

        # 5. CRITÉRIO DE SUBTÍTULO (H2)
        # Remove HTML para contar palavras reais
        texto_puro = re.sub(r"<.*?>", "", linha_limpa)
        palavras = texto_puro.split()
        
        # Se for curto e não terminar em ponto, ou se começar com #
        if (len(palavras) <= 22 and not texto_puro.endswith(".")) or linha.startswith("#"):
            html_final += f'<h2 class="subtitulo">{linha_limpa}</h2>\n'
        else:
            html_final += f'<p class="paragrafo">{linha_limpa}</p>\n'

    if em_lista: html_final += '</ul>\n' # Fecha lista se terminar o texto nela
    return html_final

def obter_esqueleto_html(dados):
    titulo = dados.get("titulo", "").strip()
    imagem = dados.get("imagem", "").strip()
    texto_bruto = dados.get("texto_completo", "")
    assinatura = dados.get("assinatura", "")

    conteudo_formatado = formatar_texto_ultra(texto_bruto, titulo)
    cfg = CONFIG_VISUAL

    return f"""
<style>
    /* CSS CENTRALIZADO E VARIÁVEL */
    .post-container {{
        max-width: {cfg['max_width']};
        margin: auto;
        font-family: {cfg['fonte_principal']} !important;
    }}

    /* Ordem 2: Título do Blogger */
    .post-title, .entry-title, h1.post-title, h3.post-title {{
        text-align: center !important;
        font-family: {cfg['fonte_principal']} !important;
        font-size: {cfg['tamanho_titulo']} !important;
        font-weight: bold !important;
        color: {cfg['cor_primaria']} !important;
        text-transform: uppercase !important;
        margin: 20px 0 !important;
    }}

    .post-img {{
        width: 100%;
        height: auto;
        aspect-ratio: 16/9;
        object-fit: cover;
        border-radius: 8px !important;
        margin-bottom: 25px;
    }}

    .subtitulo {{
        text-align: left !important;
        color: {cfg['cor_primaria']} !important;
        font-size: {cfg['tamanho_subtitulo']} !important;
        font-weight: bold !important;
        text-transform: uppercase !important;
        margin-top: 30px !important;
        margin-bottom: 12px !important;
    }}

    .paragrafo {{
        text-align: justify !important;
        color: {cfg['cor_primaria']} !important;
        font-size: {cfg['tamanho_corpo']} !important;
        line-height: 1.7 !important;
        margin-bottom: 18px !important;
    }}

    .lista-blog {{
        color: {cfg['cor_primaria']} !important;
        font-size: {cfg['tamanho_corpo']} !important;
        margin-bottom: 20px;
        padding-left: 25px;
    }}

    .lista-blog li {{
        margin-bottom: 8px;
    }}

</style>

<div class="post-container">
    <img src="{imagem}" alt="{titulo}" class="post-img">
    
    <div class="conteudo-post">
        {conteudo_formatado}
    </div>

    <div class="assinatura-container">
        {assinatura}
    </div>
</div>
"""
