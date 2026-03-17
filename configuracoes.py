# ==========================================
# CONFIGURAÇÕES GERAIS DO BLOG
# ==========================================

# Lembre-se de atualizar o BLOG_ID caso este seja um novo blog no Blogger
BLOG_ID = "4291876780757321771" 

RSS_FEEDS = [
    "https://exame.com/pme/feed/",
    "https://revistapegn.globo.com/rss/pme/",
    "https://www.infomoney.com.br/carreira/feed/",
    "https://neofeed.com.br/feed/",
    "https://ecommercenews.com.br/feed/",
    "https://resultadosdigitais.com.br/blog/feed/",
    "https://rockcontent.com/br/blog/feed/",
    "https://www.ecommercebrasil.com.br/feed/",
    "https://blog.hotmart.com/pt-br/feed/",
    "https://viverdeblog.com/feed/",
    "https://news.google.com/rss/search?q=intitle:empreendedorismo+OR+intitle:marketing+digital&hl=pt-BR&gl=BR&ceid=BR:pt-419",
    "https://news.google.com/rss/search?q=renda+extra+confiável+OR+trabalho+remoto&hl=pt-BR&gl=BR&ceid=BR:pt-419"
]

# ==========================================
# TEMAS PARA POSTAGEM CURSOS E NEGÓCIOS
# ==========================================

# Foco em Cursos, E-books e Capacitação
PALAVRAS_CURSOS_E_CONTEUDO = [
    "curso", "treinamento", "capacitação", "e-book", "infoproduto", "mentoria", 
    "workshop", "webinar", "aprendizado", "especialização", "aula", "gratuito", 
    "certificado", "formação", "estudo", "plataforma", "didática", "educativo", 
    "conhecimento", "habilidades", "venda de e-books", "produtor de conteúdo"
]

# Foco em Negócios Digitais, Afiliados e Plataformas
PALAVRAS_NEGOCIOS_DIGITAIS = [
    "Kiwify", "Hotmart", "Eduzz", "Monetizze", "afiliado", "marketing digital", 
    "vendas online", "conversão", "copywriting", "tráfego pago", "tráfego orgânico", 
    "lançamento", "funil de vendas", "estratégia", "autoridade", "branding", 
    "Instagram", "Facebook", "TikTok", "anúncios", "gestão de tráfego", "ROI"
]

# Foco em Empreendedorismo, Renda Extra e Oportunidades
PALAVRAS_OPORTUNIDADES_E_RENDA = [
    "empreendedorismo", "negócios em alta", "renda extra", "oportunidade", 
    "investimento", "carreira", "trabalho remoto", "home office", "franquia", 
    "MEI", "lucro", "escalabilidade", "monetização", "renda passiva", 
    "finanças", "pme", "inovação", "startup", "mercado", "tendência"
]

# ==========================================================
# RANKING ESTRATÉGICO DE PESOS 
# ==========================================================
PESOS_POR_TEMA = {
    "cursos": {
        "curso": 15, "gratuito": 12, "vagas": 10, "e-book": 12, "inscrição": 9,
        "especialização": 10, "treinamento": 9, "mentoria": 11, "certificado": 10
    },
    "negocios": {
        "kiwify": 15, "hotmart": 15, "monetizze": 15, "eduzz": 15, "braip": 15,
        "marketing digital": 13, "afiliado": 12, "vendas": 10, "estratégia": 9, 
        "lucro": 10, "copywriting": 11
    },
    "oportunidades": {
        "renda extra": 15, "home office": 12, "trabalho remoto": 12, "trabalho em casa": 11, 
        "mei": 10, "franquia": 11, "investimento": 9, "startup": 10, "carreira": 9, "pme": 8
    }
}

# ==========================================
# BLOCO FIXO FINAL -  ASSINATURA
# ==========================================

BLOCO_FIXO_FINAL = """
<div class="footer-marco-daher" style="background-color: #e1f5fe; border-radius: 15px; border: 1px solid rgb(179, 229, 252); color: #073763; font-family: Arial, Helvetica, sans-serif; line-height: 1.4; margin-top: 10px; padding: 25px; text-align: center;">
  
  <p style="font-size: x-small; font-weight: bold; margin-top: 0px; text-align: right;">
    <i>Por: Marco Daher<br />Todos os Direitos Reservados<br />©MarcoDaher2026</i>
  </p>

  <div class="separator" style="clear: both; margin: 15px 0px; text-align: center;">
    <a href="https://s.shopee.com.br/9zs5JZLPNm" target="_blank">
      <img border="0" height="132" src="https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEhHYBTRiztv4UNKBsiwX8nQn1M00BUz-LtO58gTZ6hEsU3VPClePhQwPWw0NyUJGqXvm3vWbRPP6LPQS6m5iyI0UQBBKmdIkNYNuXmGaxv5eMac9R6i2e9MIU7_YmWeMKntQ1ZWlzplYlDYNJr5lGHiUvwJ1CuvQOLzbOT61kF3LQ0-nD4j3Xo4HJWeOG4/w640-h132/Banner%20Shopee%20Rodap%C3%A9.gif" style="height: auto; max-width: 100%;" width="640" />
    </a>
  </div>

  <div style="margin-bottom: 20px; text-align: center;">
    <p style="font-weight: bold; margin-bottom: 10px; text-align: center;">🚀 Gostou deste conteúdo? Não guarde só para você!</p>
    <a href="https://api.whatsapp.com/send?text=Confira este artigo incrível no blog do Marco Daher!" style="background-color: #25d366; border-radius: 5px; color: white; display: inline-block; font-weight: bold; padding: 10px 20px; text-decoration: none;" target="_blank">
        Compartilhar no WhatsApp
    </a>
  </div>

  <p style="font-size: 16px; font-weight: bold; margin-bottom: 20px; text-align: center;">
    O conhecimento é o combustível para o Sucesso. Não pesa e não ocupa espaço.
  </p>

  <div style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; margin: 20px 0px;">
    <div style="border-right: 1px solid rgba(7, 55, 99, 0.2); min-width: 120px; padding: 10px;">
      <div style="color: #b45f06; font-size: 13px; font-weight: bold; margin-bottom: 5px;">Zona do Saber</div>
      <a href="http://zonadosaber1.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" title="Blogger" /></a>&nbsp;<a href="https://www.youtube.com/@ZonadoSaber51" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" title="YouTube" /></a>&nbsp;<a href="https://www.facebook.com/profile.php?id=61558194825166" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" title="Facebook" /></a>
    </div>
    <div style="border-right: 1px solid rgba(7, 55, 99, 0.2); min-width: 120px; padding: 10px;">
      <div style="color: #b45f06; font-size: 13px; font-weight: bold; margin-bottom: 5px;">MD Arte Foto</div>
      <a href="https://mdartefoto.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" /></a>&nbsp;<a href="https://www.facebook.com/mdaher51/" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" /></a>
    </div>
    <div style="border-right: 1px solid rgba(7, 55, 99, 0.2); min-width: 120px; padding: 10px;">
      <div style="color: #b45f06; font-size: 13px; font-weight: bold; margin-bottom: 5px;">DF Bolhas</div>
      <a href="https://dfbolhas.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" /></a>&nbsp;<a href="https://www.youtube.com/marcodaher51" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>&nbsp;<a href="https://www.facebook.com/mdaher51/" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" /></a>
    </div>
    <div style="border-right: 1px solid rgba(7, 55, 99, 0.2); min-width: 120px; padding: 10px;">
      <div style="color: #b45f06; font-size: 13px; font-weight: bold; margin-bottom: 5px;">Marco Daher</div>
      <a href="https://www.youtube.com/@MarcoDaher" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>&nbsp;<a href="https://www.facebook.com/MarcoDaher51/" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" /></a>
    </div>
    <div style="border-right: 1px solid rgba(7, 55, 99, 0.2); min-width: 120px; padding: 10px;">
      <div style="color: #b45f06; font-size: 13px; font-weight: bold; margin-bottom: 5px;">Diário de Notícias</div>
      <a href="https://diariodenoticias-md.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" /></a>&nbsp;<a href="https://www.youtube.com/@DiariodeNoticiasBrazuca" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>
    </div>
    <div style="border-right: 1px solid rgba(7, 55, 99, 0.2); min-width: 120px; padding: 10px;">
      <div style="color: #b45f06; font-size: 13px; font-weight: bold; margin-bottom: 5px;">Emagrecer com Saúde</div>
      <a href="https://emagrecendo100crise.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" /></a>&nbsp;<a href="https://www.youtube.com/@Saude-Bem-Estar-51" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>&nbsp;<a href="https://www.facebook.com/marcocuidese" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" title="Facebook" /></a>
    </div>
    <div style="border-right: 1px solid rgba(7, 55, 99, 0.2); min-width: 120px; padding: 10px;">
      <div style="color: #b45f06; font-size: 13px; font-weight: bold; margin-bottom: 5px;">Relaxamento</div>
      <a href="https://www.youtube.com/channel/UCRNq9fN3jzLt0JeE5yBsqQQ" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>
    </div>
    <div style="min-width: 120px; padding: 10px;">
      <div style="color: #b45f06; font-size: 13px; font-weight: bold; margin-bottom: 5px;">Cursos e Negócios</div>
      <a href="https://cursosnegocioseoportunidades.blogspot.com/" target="_blank"><img src="https://img.icons8.com/color/48/000000/blogger.png" style="height: 32px; width: 32px;" /></a>&nbsp;<a href="https://www.youtube.com/@CursoseNegociosMD" target="_blank"><img src="https://img.icons8.com/color/48/000000/youtube-play.png" style="height: 32px; width: 32px;" /></a>&nbsp;<a href="https://www.facebook.com/CursosNegociosOportunidades" target="_blank"><img src="https://img.icons8.com/color/48/000000/facebook-new.png" style="height: 32px; width: 32px;" /></a>
    </div>
  </div>
<hr style="border-bottom: 0px; border-image: initial; border-left: 0px; border-right: 0px; border-top: 1px solid rgba(7, 55, 99, 0.133); border: 0px; margin: 20px 0px;" />
  <p style="font-size: 14px; font-weight: bold; margin-bottom: 10px;">
    Caso queira contribuir com o meu Trabalho, use a CHAVE PIX abaixo:
  </p>
  <button onclick="navigator.clipboard.writeText('marco.caixa104@gmail.com'); alert('Chave PIX copiada!');" style="background-color: #0288d1; border-color: initial; border-radius: 8px; border-style: none; border-width: initial; box-shadow: rgba(0, 0, 0, 0.2) 0px 2px 4px; color: white; cursor: pointer; font-size: 14px; font-weight: bold; padding: 12px 20px; transition: 0.3s;">
    Copiar Chave PIX: marco.caixa104@gmail.com
  </button>
</div>
<hr data-end="883" data-start="880" style="text-align: justify;" />
<h2 data-end="913" data-start="885" style="text-align: justify;"><br /></h2>
"""
