import os
import pandas as pd
from tqdm import tqdm
import json
import re # NOVO: Importa a biblioteca de expressões regulares

from data.database import get_all_articles, close_ssh_tunnel
from prompt import prompt_template_simplificado

# --- Configuração do Modelo de Linguagem (LLM) ---
from langchain_community.chat_models import ChatOllama
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

llm = ChatOllama(
    model="phi3:latest",
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
    
    print(f"Iniciando a extração para {len(sentences)} artigos.")
    
    for i in tqdm(range(len(sentences)), desc="Extraindo e Processando com LLM"):
        article_text = sentences[i]
        article_id = article_ids[i]
        
        if not article_text or not isinstance(article_text, str):
            continue
            
        try:
            response_str = chain.run({'input_noticia': article_text})
            
            # --- LÓGICA DE LIMPEZA APRIMORADA ---
            # Usa expressões regulares para encontrar o bloco JSON na resposta,
            # que pode conter texto extra antes ou depois.
            match = re.search(r'\{.*\}', response_str, re.DOTALL)
            
            if match:
                clean_json_str = match.group(0)
                # Analisa a string JSON extraída
                data = json.loads(clean_json_str)
                
                # Adiciona o ID do artigo
                data['_id'] = article_id
                
                extracted_data_list.append(data)
            else:
                # Se nenhum JSON for encontrado na resposta
                print(f"\nAVISO: Nenhum JSON válido encontrado na resposta para o artigo {article_id}.")
                extracted_data_list.append({'_id': article_id, 'erro': 'no_json_found', 'resposta_bruta': response_str})

        except json.JSONDecodeError as e:
            # Este erro agora ocorrerá se o bloco extraído ainda for um JSON inválido
            print(f"\nAVISO: Erro de decodificação JSON para o artigo {article_id}.")
            print(f"   - Bloco JSON extraído: {clean_json_str}")
            extracted_data_list.append({'_id': article_id, 'erro': 'json_decode_error', 'resposta_bruta': response_str})
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
            
        output_filename = 'phi3:latest'
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
            
            sentences = df_relevant_articles['article'].head(10).tolist() # Aumentei para 10 para um teste melhor
            article_ids = df_relevant_articles['_id'].head(10).tolist()
            print(f"Total de {len(sentences)} textos prontos para processamento (limite de teste).")

            extract_and_process_features(article_ids, sentences)
            
            print("\nFluxo de trabalho concluído com sucesso.")

    except Exception as e:
        print(f"\nOcorreu um erro durante a execução: {e}")
        
    finally:
        print("\nFechando a conexão com o banco de dados...")
        close_ssh_tunnel()
        print("Conexão fechada.")