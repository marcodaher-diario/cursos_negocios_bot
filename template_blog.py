# -*- coding: utf-8 -*-
import re

# ==========================================================
# CONFIGURAÇÃO DE IDENTIDADE VISUAL (CORINGA V3.1)
# ==========================================================
CONFIG_VISUAL = {
    "cor_md": "rgb(7, 55, 99)",
    "fonte": "Open Sans", 
    "tamanho_titulo": "28px",
    "tamanho_sub": "22px",
    "tamanho_texto": "18px"
}

def formatar_texto_ultra(texto_bruto, titulo_principal):
    if not texto_bruto: return ""
    linhas = [l.strip() for l in texto_bruto.split("\n") if l.strip()]
    html_final = ""
    titulo_norm = titulo_principal.strip().lower()
    em_lista = False

    for linha in linhas:
        # Markdown Simples
        linha = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", linha)
        linha = re.sub(r"(?<!\*)\*(?!\*)(.*?)\*", r"<em>\1</em>", linha)
        
        # Listas
        match_lista = re.match(r"^([\*\-\•]|\d+\.)\s*(.*)", linha)
        if match_lista:
            conteudo_item = match_lista.group(2)
            if not em_lista:
                html_final += '<ul style="margin-bottom:20px; padding-left:30px;">\n'
                em_lista = True
            html_final += f'  <li style="color:{CONFIG_VISUAL["cor_md"]}; font-size:{CONFIG_VISUAL["tamanho_texto"]}; margin-bottom:10px;">{conteudo_item}</li>\n'
            continue
        else:
            if em_lista:
                html_final += '</ul>\n'
                em_lista = False

        linha_limpa = linha.lstrip("# ").strip()
        if linha_limpa.lower() == titulo_norm or not linha_limpa: continue

        texto_para_contagem = re.sub(r"<.*?>", "", linha_limpa)
        palavras = texto_para_contagem.split()
        
        # Subtítulos H2 com Estilo Direto (Garante que funcione sempre)
        if (len(palavras) <= 22 and not texto_para_contagem.endswith(".")) or linha.startswith("#"):
            html_final += f"""
            <h2 style="text-align:left !important; color:{CONFIG_VISUAL['cor_md']} !important; font-family:{CONFIG_VISUAL['fonte']} !important; font-size:{CONFIG_VISUAL['tamanho_sub']} !important; text-transform:uppercase !important; margin-top:30px !important; margin-bottom:12px !important; display:block !important; clear:both !important; -webkit-font-smoothing: antialiased !important;">
                {linha_limpa}
            </h2>\n"""
        else:
            # Parágrafos com Estilo Direto
            html_final += f"""
            <p style="text-align:justify !important; color:{CONFIG_VISUAL['cor_md']} !important; font-family:{CONFIG_VISUAL['fonte']} !important; font-size:{CONFIG_VISUAL['tamanho_texto']} !important; line-height:1.6 !important; margin-bottom:15px !important;">
                {linha_limpa}
            </p>\n"""

    if em_lista: html_final += '</ul>\n'
    return html_final

def obter_esqueleto_html(dados):
    titulo = dados.get("titulo", "").strip()
    imagem = dados.get("imagem", "").strip()
    texto_bruto = dados.get("texto_completo", "")
    assinatura = dados.get("assinatura", "")
    conteudo_formatado = formatar_texto_ultra(texto_bruto, titulo)
    c = CONFIG_VISUAL

    # Voltamos ao estilo Inline para os Títulos para garantir que o Blogger não ignore
    return f"""
<div style="max-width:900px; margin:auto; font-family:{c['fonte']};">
    
    <style>
        .post-title, .entry-title, h1.post-title, h3.post-title {{
            text-align: center !important;
            font-size: {c['tamanho_titulo']} !important;
            font-weight: bold !important;
            color: {c['cor_md']} !important;
            text-transform: uppercase !important;
            margin: 10px 0 25px 0 !important;
        }}
    </style>

    <div style="text-align:center; margin-bottom:30px;">
        <img src="{imagem}" alt="{titulo}" style="width:100%; height:auto; aspect-ratio:16/9; object-fit:cover; border-radius:8px;">
    </div>

    <div class="corpo-post-coringa">
        {conteudo_formatado}
    </div>

    <div style="margin-top:40px; border-top:1px solid #eee; padding-top:20px;">
        {assinatura}
    </div>
</div>
"""
