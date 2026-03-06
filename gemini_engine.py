# -*- coding: utf-8 -*-

import os
import re
import time
from google import genai
from google.api_core import exceptions

class GeminiEngine:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)
        # Estratégia de Fallback solicitada: 3 Modelos em 3 Ciclos
        self.modelos_fallback = [
            "gemini-3-flash-preview",
            "gemini-2.5-pro", 
            "gemini-2.5-flash"
        ]

    def _limpar_e_formatar_markdown(self, texto):
        """
        Mantido EXATAMENTE como no seu original:
        Transforma negritos Markdown em HTML <strong> e remove marcadores de título e lista.
        """
        if not texto:
            return ""
            
        # 1. Transforma **texto** em <strong>texto</strong>
        texto = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', texto)
        
        # 2. Suprime os marcadores de título #, ##, ###, etc.
        texto = re.sub(r'#+\s?', '', texto)
        
        # 3. Suprime asteriscos isolados (marcadores de lista ou itálico simples)
        texto = re.sub(r'^\s*\*\s?', '', texto, flags=re.MULTILINE)
        texto = texto.replace('*', '')
        
        return texto.strip()

    def _executar_com_resiliencia(self, prompt):
        """
        Lógica de 9 tentativas (3 ciclos x 3 modelos) 
        sem alterar os prompts originais.
        """
        tentativa_total = 1
        for ciclo in range(1, 4):  # 3 passagens completas
            for modelo in self.modelos_fallback:
                try:
                    print(f"Tentativa {tentativa_total}/9 | Ciclo {ciclo} | Usando: {modelo}")
                    
                    response = self.client.models.generate_content(
                        model=modelo,
                        contents=prompt
                    )

                    if response and hasattr(response, 'text') and response.text:
                        return response.text
                
                except Exception as e:
                    erro_msg = str(e).upper()
                    # Identifica se o erro é de "Lotado" (503), "Timeout" ou "Cota"
                    if any(x in erro_msg for x in ["503", "UNAVAILABLE", "DEADLINE", "429", "QUOTA"]):
                        print(f"⚠️ Modelo {modelo} indisponível ou lotado. Pulando para o próximo...")
                        time.sleep(5) # Pausa curta antes da próxima tentativa
                    else:
                        print(f"❌ Erro crítico no modelo {modelo}: {e}")
                
                tentativa_total += 1
        
        return None

# ==========================================================
# GERAR ANALISE JORNALISTICA BASEADO NA CATEGORIA
# ==========================================================

    def gerar_analise_jornalistica(self, titulo, resumo, categoria):
        """
        Gera o artigo principal seguindo o tom da Forbes/Exame focado no Brasil.
        """
        prompt = f"""
Atue como um Estrategista de Negócios Digitais e Especialista em Marketing Digital com 20 anos de experiência no mercado brasileiro de Infoprodutos e Empreendedorismo.

Seu objetivo: Redigir um artigo educativo e estratégico baseado nas informações fornecidas. O texto deve seguir o padrão de autoridade da Forbes Brasil ou Exame, com foco total no cenário econômico e digital do BRASIL.

Informações base:
Título da notícia/tema: {titulo}
Resumo da notícia/tema: {resumo}
Categoria: {categoria}

DIRETRIZES DE LOCALIZAÇÃO (FOCO BRASIL):
1. RESTRITO AO BRASIL: Ignore qualquer contexto geopolítico ou social que não afete diretamente o empreendedor brasileiro. Se a notícia base for internacional, você DEVE obrigatoriamente tropicalizar o conteúdo, explicando o impacto direto no mercado interno (PIB, dólar, comportamento de consumo do brasileiro ou plataformas locais).
2. ECOSSISTEMA LOCAL: Cite, quando pertinente, a realidade de quem utiliza plataformas como Kiwify, Hotmart, Eduzz, Monetizze, Braip e o cenário de MEI/PMEs no Brasil.
3. LINGUAGEM: Use português do Brasil, com termos técnicos de marketing digital adotados no país.

DIRETRIZES OBRIGATÓRIAS DE CONTEÚDO:
- Tom e Estilo: Profissional, educativo e analítico. Evite sensacionalismo e promessas de "dinheiro rápido".
- Extensão: Entre 600 e 800 palavras. Desenvolva parágrafos densos e com insights práticos.
- Originalidade: Transforme a notícia em uma análise consultiva. O leitor deve terminar a leitura sabendo "o que fazer agora" no seu negócio no Brasil.

ESTRUTURA DO TEXTO:
1. Título: Estratégico, focado em análise de mercado para brasileiros.
2. Lide (Lead): Conecte o fato imediatamente à realidade dos negócios digitais ou carreiras no Brasil.
3. Subtítulos: Organize com pelo menos dois subtítulos (ex: "Desafios no Cenário Nacional" e "Estratégias de Adaptação").
4. Corpo: Explique o "porquê" por trás dos dados com viés consultivo para produtores, afiliados ou estudantes brasileiros.
5. Conclusão Analítica: Visão estratégica sobre o futuro da tendência no Brasil e incentivo à profissionalização.

Importante:
- Proibido mencionar eventos estrangeiros que não possuam correlação direta e explicada com o Brasil.
- Não escreva explicações externas ou observações adicionais.
- Entregue apenas o texto final estruturado.
"""
        # Executa o prompt usando a lógica de resiliência (os 3 modelos que você validou)
        resultado = self._executar_com_resiliencia(prompt)

        if resultado:
            return self._limpar_e_formatar_markdown(resultado)
        
        return "Erro: Falha total da API após 9 tentativas ao gerar artigo"

# ==========================================================
# GERAR QUERY VISUAL PARA BUSCA DE IMAGENS
# ==========================================================

    def gerar_query_visual(self, titulo, resumo):
        """
        Gera uma query de busca em inglês otimizada para Pexels/Unsplash 
        com base no contexto da notícia.
        """
        prompt = f"""
Com base no título e resumo abaixo, gere APENAS uma sequência de 3 a 4 palavras-chave 
em INGLÊS que descrevam uma imagem fotográfica de alta qualidade (estilo editorial/business) 
ideal para ilustrar esta matéria em um blog de negócios e cursos.

Diretrizes:
- Aspect Ratio: 16:9 (obrigatório).
- Estética: Profissional, moderna, clean e corporativa.
- Foque em elementos visuais: (ex: "laptop workspace coffee", "digital marketing analytics", "entrepreneur thinking office", "online education student").
- Use apenas substantivos e adjetivos visuais em INGLÊS.
- Não use verbos ou frases completas.
- Retorne APENAS as palavras em inglês, sem pontuação extra.

Notícia: {titulo}
Resumo: {resumo}
"""
        resultado = self._executar_com_resiliencia(prompt)

        if resultado:
            texto_puro = resultado.strip()
            return self._limpar_e_formatar_markdown(texto_puro)
        
        return "business workspace professional"
