# -*- coding: utf-8 -*-
import re

def formatar_conteudo_inteligente(texto_bruto, titulo_principal):
    if not texto_bruto: return ""
    
    linhas = [l.strip() for l in texto_bruto.split("\n") if l.strip()]
    html_final = []
    titulo_norm = titulo_principal.strip().lower()
    lista_aberta = False

    for linha in linhas:
        # 1. Conversão de Negritos e Itálicos (Markdown para HTML)
        l_proc = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", linha)
        l_proc = re.sub(r"\*(.*?)\*", r"<em>\1</em>", l_proc)
        
        # 2. Limpeza de marcadores Markdown (# e *)
        l_limpa = l_proc.lstrip("#* ").strip()
        
        # 3. Filtro Anti-Repetição do Título
        if l_limpa.lower() == titulo_norm or not l_limpa:
            continue

        # 4. Tratamento de Listas (UL/LI)
        if linha.startswith(("- ", "* ")) or re.match(r"^\d+\.", linha):
            if not lista_aberta:
                html_final.append('<ul class="lst">')
                lista_aberta = True
            item = re.sub(r"^[-*\d. ]+", "", l_limpa)
            html_final.append(f'<li>{item}</li>')
            continue
        else:
            if lista_aberta:
                html_final.append('</ul>')
                lista_aberta = False

        # 5. DETECÇÃO DE HIERARQUIA (H1, H2, H3)
        # Contagem de palavras para diferenciar título de parágrafo
        texto_puro = re.sub(r"<.*?>", "", l_limpa)
        palavras = texto_puro.split()
        
        # Critério: Se começa com # (Markdown) ou é curto e sem ponto final
        e_titulo = (linha.startswith("#") or (len(palavras) <= 15 and not texto_puro.endswith((".", ":", "?", "!"))))

        if e_titulo:
            # H1 Manual (Se o usuário usar # no texto)
            if linha.startswith("# "):
                html_final.append(f'<h1 class="t1">{l_limpa}</h1>')
            # H2 (Padrão para seções ou ##)
            elif linha.startswith("## ") or not linha.startswith("### "):
                html_final.append(f'<h2 class="t2">{l_limpa}</h2>')
            # H3 (Subseções ou ###)
            else:
                html_final.append(f'<h3 class="t3">{l_limpa}</h3>')
        else:
            # 6. Parágrafo Normal
            html_final.append(f'<p class="txt">{l_limpa}</p>')

    if lista_aberta: html_final.append('</ul>')
    return "\n".join(html_final)

def obter_esqueleto_html(dados):
    t = dados.get("titulo", "").strip()
    img = dados.get("imagem", "").strip()
    txt = dados.get("texto_completo", "")
    ass = dados.get("assinatura", "")
    
    cor = "rgb(7, 55, 99)"

    return f"""
<style>
/* Container Principal */
.post-master {{ max-width:900px; margin:auto; font-family:sans-serif; color:{cor}; line-height:1.6; }}

/* Títulos Automáticos do Blogger (H1/H3 dependendo do tema) */
.post-title, .entry-title, h1.post-title {{
    text-align:center!important; font-size:28px!important; text-transform:uppercase!important; 
    font-weight:bold!important; margin:10px 0 25px 0!important; color:{cor}!important;
}}

/* Imagem 16:9 Responsiva */
.img-c {{ text-align:center; margin-bottom:25px; }}
.img-p {{ width:100%; height:auto; aspect-ratio:16/9; object-fit:cover; border-radius:8px; }}

/* Hierarquia de Títulos no Corpo do Texto */
.t1 {{ font-size:26px!important; font-weight:bold!important; text-align:center!important; margin:30px 0 15px 0!important; text-transform:uppercase!important; color:{cor}!important; }}
.t2 {{ font-size:22px!important; font-weight:bold!important; text-align:left!important; margin:30px 0 12px 0!important; text-transform:uppercase!important; color:{cor}!important; }}
.t3 {{ font-size:19px!important; font-weight:bold!important; text-align:left!important; margin:25px 0 10px 0!important; color:{cor}!important; }}

/* Parágrafos e Listas */
.txt {{ font-size:18px!important; text-align:justify!important; margin-bottom:15px!important; color:{cor}!important; }}
.lst {{ margin-bottom:20px; padding-left:25px; }}
.lst li {{ font-size:18px!important; margin-bottom:8px; color:{cor}!important; }}

/* Assinatura */
.sig {{ margin-top:35px; border-top:1px solid #eee; padding-top:20px; font-style:italic; }}
</style>

<div class="post-master">
    <div class="img-c"><img src="{img}" alt="{t}" class="img-p" loading="lazy"></div>
    <div class="conteudo-principal">
        {formatar_conteudo_inteligente(txt, t)}
    </div>
    <div class="sig">{ass}</div>
</div>
"""
