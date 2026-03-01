# -*- coding: utf-8 -*-

import os
from google import genai


class GeminiEngine:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)

    def gerar_analise_jornalistica(self, titulo, resumo, categoria):

        prompt = f"""
Atue como um Estrategista de Negócios Digitais e Especialista em Marketing com 20 anos de experiência em Infoprodutos e Empreendedorismo.

Seu objetivo: Redigir um artigo educativo e estratégico baseado nas informações que fornecerei abaixo. O texto deve seguir padrões de qualidade de portais como Harvard Business Review ou Forbes, com foco em autoridade e confiança.

Informações base:

Título da notícia/tema: {titulo}

Resumo da notícia/tema: {resumo}

Categoria: {categoria}

Diretrizes Obrigatórias:

Tom e Estilo: Profissional, educativo e persuasivo (conversão moderada). Use linguagem clara, que demonstre autoridade no nicho de negócios, evitando promessas de ganho fácil.

Extensão: Entre 700 palavras no mínimo e 900 palavras no máximo. Desenvolva os parágrafos com profundidade e insights acionáveis.

Originalidade: O texto deve ser inédito, processando as informações e transformando notícias em guias, análises de mercado ou oportunidades de aprendizado.

Foco: Priorizar o valor para o leitor, explicando como ele pode aplicar aquela informação em sua carreira, curso ou negócio digital (Kiwify, Hotmart, etc).

Estrutura do Texto:

Título: Estratégico, focado em benefício ou análise de mercado (atraente para empreendedores).

Lide (Lead): O primeiro parágrafo deve situar o leitor sobre a oportunidade ou mudança no mercado, conectando o fato à realidade dos negócios digitais.

Subtítulos: Utilize pelo menos dois subtítulos para organizar o conteúdo (ex: "Impactos no Mercado" e "Passos Práticos" ou "Análise da Oportunidade").

Corpo: Desenvolva os fatos com um viés consultivo. Explique o "porquê" por trás dos dados e como isso afeta produtores, afiliados ou estudantes.

Conclusão Analítica: Encerre com uma visão estratégica sobre o futuro dessa tendência e um incentivo à profissionalização e estudo contínuo.

Importante:
- Não escreva explicações externas.
- Não inclua observações adicionais.
- Entregue apenas o texto final já estruturado.
"""

        response = self.client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )

        return response.text.strip()

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

        try:
            response = self.client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt
            )
            return response.text.strip().replace('"', '').replace("'", "")
        except:
            return None
