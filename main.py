import os
os.environ["GOOGLE_API_KEY"] = "AIzaSyC1e83Fydo1ACe6pH34X15Y52ubwhDqdZA"
import time # Importa a biblioteca 'time' para usar a função sleep
import pandas as pd
from tqdm import tqdm

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

from data.database import get_all_articles, close_ssh_tunnel #
from prompt import prompt_template #

def fetch_relevant_articles() -> pd.DataFrame:
    """
    Busca todas as notícias no banco de dados e filtra aquelas classificadas
    como relevantes, seja manual ou automaticamente.
    """
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
        return pd.DataFrame()

    print(f"\nTotal de {len(relevant_articles_list)} notícias relevantes encontradas.")
    
    df_relevant = pd.DataFrame(relevant_articles_list)
    return df_relevant

def extract_features(article_ids: list, sentences: list):
    """
    Processa cada texto de notícia para extrair características estruturadas
    utilizando um Modelo de Linguagem Amplo (LLM).
    """
    print("\n--- Iniciando Fase 2: Extração de Características ---")
    if not sentences:
        print("Nenhum texto de artigo para processar.")
        return

    # 1. Configuração do LLM
    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        temperature=0.0
    )
    # 2. Configuração do Prompt e Parser
    output_parser = StrOutputParser()
    # 3. Criação da Cadeia (Chain) de Extração
    chain = prompt_template | llm | output_parser
    
    # 4. Iteração e Extração
    print(f"Iniciando a extração de características para {len(sentences)} artigos.")
    extracted_data_list = []
    
    for i in tqdm(range(len(sentences)), desc="Extraindo com LLM"):
        # ---- CONTROLE DE LIMITE DE REQUISIÇÃO ADICIONADO ----
        # A cada 15 requisições, pausa por 61 segundos para resetar o limite da API.
        if i > 0 and i % 15 == 0:
            print(f"\nLimite de 15 requisições atingido. Pausando por 61 segundos...")
            time.sleep(61)
            print("Continuando a extração...")

        article_text = sentences[i]
        article_id = article_ids[i]
        
        if not article_text or not isinstance(article_text, str):
            continue
            
        try:
            extracted_data = chain.invoke({"input_noticia": article_text})
            extracted_data_list.append({
                '_id': article_id,
                'dados_extraidos': extracted_data,
                'erro': None
            })
        except Exception as e:
            print(f"Erro ao processar artigo {article_id}: {e}")
            extracted_data_list.append({
                '_id': article_id,
                'dados_extraidos': None,
                'erro': str(e)
            })

    print("Extração concluída.")

    # 5. Salvando os resultados
    if extracted_data_list:
        df_final = pd.DataFrame(extracted_data_list)
        output_filename = 'caracteristicas_extraidas.csv'
        df_final.to_csv(output_filename, index=False, encoding='utf-8-sig')
        print(f"\nResultados da extração foram salvos em '{output_filename}'")
    
    print("----------------------------------------------------")

# Bloco principal de execução do script
if __name__ == "__main__":
    if "GOOGLE_API_KEY" not in os.environ:
        print("ERRO: A variável de ambiente GOOGLE_API_KEY não foi definida.")
        exit()

    try:
        df_relevant_articles = fetch_relevant_articles()
        
        if not df_relevant_articles.empty:
            print("\nExtraindo textos dos artigos para a próxima fase...")
            sentences = df_relevant_articles['article'].tolist()
            article_ids = df_relevant_articles['_id'].tolist()
            print(f"Total de {len(sentences)} textos prontos para processamento.")

            extract_features(article_ids, sentences)
            
            print("\nFluxo de trabalho concluído com sucesso.")

    except Exception as e:
        print(f"\nOcorreu um erro durante a execução: {e}")
    finally:
        print("\nFechando a conexão com o banco de dados...")
        close_ssh_tunnel()
        print("Conexão fechada.")