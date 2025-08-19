# main_simplificado.py

import os
import pandas as pd
from tqdm import tqdm
import json # Usaremos para tentar carregar listas como 'Drogas Apreendidas'

from data.database import get_all_articles, close_ssh_tunnel
from prompt_simplificado import prompt_template_simplificado

# --- Configuração do Modelo de Linguagem (LLM) ---
from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

llm = ChatOllama(
    model="brunoconterato/Gemma-3-Gaia-PT-BR-4b-it:f16",
    base_url="http://127.0.0.1:11434",
    temperature=0.0
)

prompt = PromptTemplate(
    input_variables=["input_noticia"],
    template=prompt_template_simplificado,
)

chain = LLMChain(llm=llm, prompt=prompt)


def extract_and_process_features(article_ids: list, sentences: list):
    """
    Processa cada texto de notícia para extrair características,
    processa a saída formatada do LLM e gera um CSV estruturado.
    """
    print("\n--- Iniciando Extração e Processamento de Características ---")
    if not sentences:
        print("Nenhum texto de artigo para processar.")
        return

    extracted_data_list = []
    # Cabeçalhos definidos na ordem exata do prompt
    headers = [
        "Organizacao Criminosa", "Pais", "Estado", "Municipio", "Data", "Houve Conflito",
        "Apreensao de Drogas", "Drogas Apreendidas", "Quantidade de Drogas",
        "Apreensao de Armas", "Armas Apreendidas", "Primeiro Ator", "Segundo Ator",
        "Relacao Entre Atores"
    ]
    
    print(f"Iniciando a extração para {len(sentences)} artigos.")
    
    for i in tqdm(range(len(sentences)), desc="Extraindo e Processando com LLM"):
        article_text = sentences[i]
        article_id = article_ids[i]
        
        if not article_text or not isinstance(article_text, str):
            continue
            
        try:
            # O LLM agora retorna uma string separada por ';'
            response_str = chain.run({'input_noticia': article_text})
            
            # Divide a string nos valores
            values = response_str.strip().split(';')
            
            # Cria um dicionário combinando cabeçalhos e valores
            if len(values) == len(headers):
                processed_data = dict(zip(headers, values))
                processed_data['_id'] = article_id  # Adiciona o ID
                extracted_data_list.append(processed_data)
            else:
                print(f"\nAVISO: Erro de formatação na resposta para o artigo {article_id}. Número de campos não corresponde ao esperado.")
                print(f"   - Resposta recebida: {response_str}")
                # Adiciona uma entrada de erro para não perder a referência
                extracted_data_list.append({'_id': article_id, 'erro': 'formato_invalido', 'resposta_bruta': response_str})

        except Exception as e:
            print(f"\nErro ao processar artigo {article_id}: {e}")
            extracted_data_list.append({
                '_id': article_id,
                'dados_extraidos': None,
                'erro': str(e)
            })

    print("Extração concluída.")

    if extracted_data_list:
        df_final = pd.DataFrame(extracted_data_list)
        
        # Garante que a coluna '_id' seja a primeira
        if '_id' in df_final.columns:
            cols = ['_id'] + [col for col in df_final.columns if col != '_id']
            df_final = df_final[cols]
            
        output_filename = 'caracteristicas_extraidas_processado.csv'
        df_final.to_csv(output_filename, index=False, encoding='utf-8-sig')
        print(f"\nResultados processados e salvos em '{output_filename}'")
    
    print("----------------------------------------------------")


# Bloco principal de execução do script
if __name__ == "__main__":
    try:
        print("Iniciando a busca por notícias relevantes no banco de dados...")
        articles_cursor = get_all_articles()
        
        relevant_articles_list = []
        
        print("Processando e filtrando artigos...")
        for article in tqdm(articles_cursor, desc="Filtrando notícias relevantes"):
            manual_class = article.get('manual_relevance_class')
            auto_class = article.get('automatic_relevance_class')
            
            if manual_class == 1 or auto_class == 1:
                relevant_articles_list.append(article)
                
        if not relevant_articles_list:
            print("\nNenhuma notícia relevante foi encontrada.")
        else:
            df_relevant_articles = pd.DataFrame(relevant_articles_list)
            
            print("\nExtraindo textos dos artigos para a próxima fase...")
            
            # --- PONTO IMPORTANTE ---
            # O código abaixo seleciona apenas as 5 primeiras notícias para o teste.
            # O .head(5) faz a limitação.
            sentences = df_relevant_articles['article'].head(5).tolist()
            article_ids = df_relevant_articles['_id'].head(5).tolist()
            print(f"Total de {len(sentences)} textos prontos para processamento (limite de teste).")

            extract_and_process_features(article_ids, sentences)
            
            print("\nFluxo de trabalho concluído com sucesso.")

    except Exception as e:
        print(f"\nOcorreu um erro durante a execução: {e}")
        
    finally:
        print("\nFechando a conexão com o banco de dados...")
        close_ssh_tunnel()
        print("Conexão fechada.")