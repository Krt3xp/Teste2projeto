from sshtunnel import open_tunnel, SSHTunnelForwarder
from pymongo import MongoClient, UpdateOne
from datetime import datetime
import threading
import pymongo
import socket
import yaml

# Leitura do arquivo de credenciais
configs_file = open('config.yml', 'r')
configs = yaml.safe_load(configs_file)
configs_file.close()

server = None
db_client = None
tunnel_timer = None

def is_tunnel_open() -> bool:
    """
    Verifica se há conexão com o servidor.
    """
    return (not server is None) and server.is_active

def open_ssh_tunnel(timeout_minutes=10) -> MongoClient:
    """
    Abre o túnel SSH onde está o MongoDB e retorna o cliente do banco.
    Se não houver novas interações, o túnel é fechado em `timeout_minutes`.
    """
    global db_client, tunnel_timer, server

    if not is_tunnel_open():
        server = SSHTunnelForwarder(
            (configs["lamcad"]["server_ip"], configs["lamcad"]["server_port"]),
            ssh_username=configs["lamcad"]["ssh_username"],
            ssh_password=configs['lamcad']['ssh_password'],
            local_bind_address=("localhost", 27018),
            remote_bind_address=("127.0.0.1", 27017),
        )
        server.start()
        db_client = pymongo.MongoClient(configs["mongodb_lamcad"]["uri"])

    # Reiniciando o timer
    if tunnel_timer is not None:
        tunnel_timer.cancel()
    tunnel_timer = threading.Timer(timeout_minutes * 60, close_ssh_tunnel)
    tunnel_timer.start()

    return db_client

def close_ssh_tunnel():
    """
    Encerra a conexão SSH.
    """
    # if not server is None:
    #     server.close()
    global db_client, tunnel_timer, server

    if server is not None:
        server.stop()
        server = None

    if db_client is not None:
        db_client.close()
        db_client = None
    
    if tunnel_timer is not None:
        tunnel_timer.cancel()
        tunnel_timer = None

def get_articles(n=None, only_manually_classified=True, relevants=True):
    """
    Função que obtém `n` notícias aleatórias assinaladas manualmente como relevantes (`relevants=True`)
    ou não relevantes (`relevants=False`)
    Apenas os valores dos campos "_id", "url", "newspaper", title" e "article" são retornados.
    """
    db_client = open_ssh_tunnel()
    collection = db_client["couser"]["newsData"]

    pipeline = []

    if only_manually_classified:
        pipeline.append({'$match': {'manual_relevance_class': int(relevants)}})

    pipeline.append(
        {'$project': {
            '_id': 1,
            'newspaper': 1,
            'url': 1,
            'title': 1,
            'article': 1,
            'manual_relevance_class': 1,
        }}
    )
    if n:
        pipeline.append({"$sample": {"size": n}})
    articles = list(collection.aggregate(pipeline))
    # close_ssh_tunnel(server)
    return articles

def get_all_articles(batch_size=100, limit=None):
    """
    Função que obtém todas as notícias da coleção `newsData` do MongoDB.
    """
    db_client = open_ssh_tunnel()
    collection = db_client["couser"]["newsData"]

    cursor = collection.find(
        {}, {
        '_id': 1,
        'newspaper': 1,
        'url': 1,
        'title': 1,
        'article': 1,
        'manual_relevance_class': 1,
        'automatic_relevance_class': 1,
    }).batch_size(batch_size)

    if limit:
        cursor = cursor.limit(limit)  # Apply limit if specified

    count = 0
    for article in cursor:
        yield article  # Yield each article lazily
        count += 1
        if limit and count >= limit:
            break  # Stop iterating when the limit is reached

def pipeline_exists(pipeline) -> bool:
    """
    Verifica se o pipeline já existe no banco de dados.
    """
    db_client = open_ssh_tunnel()
    collection = db_client["couser"]["classification_pipelines"]

    pipeline_named_steps = {name: str(step) for name, step in pipeline.named_steps.items()}

    result = collection.find_one({'named_steps': pipeline_named_steps})

    return bool(result)

def save_classification_pipeline(pipeline_id, pipeline, score):
    """
    Salva o pipeline de classificação no banco de dados.
    """
    db_client = open_ssh_tunnel()
    collection = db_client["couser"]["classification_pipelines"]

    # Obtenção da data atual
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Extração dos passos do pipeline
    named_steps = {name: str(step) for name, step in pipeline.named_steps.items()}

    if pipeline_exists(pipeline):
        collection.update_one(
            {"pipeline_id": pipeline_id},
            {"$set": {
                "timestamp": timestamp,
                "named_steps": named_steps,
                "score": round(score, 4)
                }
            }
        )
    else:
        collection.insert_one({
            "timestamp": timestamp,
            "pipeline_id": pipeline_id,
            "named_steps": named_steps,
            "score": round(score, 4)
        })

def get_best_classification_pipeline_id():
    """
    Obtém o ID do pipeline de classificação com a melhor pontuação.
    """
    db_client = open_ssh_tunnel()
    collection = db_client["couser"]["classification_pipelines"]

    best_pipeline_id = collection.find_one({}, sort=[("score", -1)])["pipeline_id"]

    return best_pipeline_id

def update_articles(updates, batch_size=100):
    """
    Atualiza os documentos no MongoDB com os dados fornecidos.
    """
    db_client = open_ssh_tunnel()
    collection = db_client["couser"]["newsData"]

    batch = []
    for _id, update in updates:
        batch.append(UpdateOne({"_id": _id}, {"$set": update}))

        if len(batch) >= batch_size:
            collection.bulk_write(batch)
            batch.clear()

    # Execução do batch final
    if batch:
        collection.bulk_write(batch)
        batch.clear()

def convert_publication_dates():
    """
    Converte o campo 'publication_date' de string para datetime em todos os documentos da coleção.
    """
    db_client = open_ssh_tunnel()
    collection = db_client["couser"]["newsData"]

    updates = []
    batch_size = 1000
    cursor = collection.find({"publication_date": {"$type": "string"}}, {"publication_date": 1})

    for doc in cursor:
        try:
            date_str = doc["publication_date"]
            # parsed_date = datetime.strptime(date_str, "%d-%m-%Y")
            parsed_date = datetime.strptime(date_str, "%Y-%m-%d") # Correio do povo
            updates.append(UpdateOne({"_id": doc["_id"]}, {"$set": {"publication_date": parsed_date}}))
        except (ValueError, KeyError):
            continue  # pula documentos com datas inválidas ou campo ausente

        if len(updates) >= batch_size:
            print(f"Atualizando {len(updates)} documentos...")
            collection.bulk_write(updates)
            updates = []

    # Escrita final se restarem atualizações
    if updates:
        collection.bulk_write(updates)

    print("Conversão de datas concluída.")

if __name__ == "__main__":
    client = open_ssh_tunnel()
    print("Túnel SSH aberto!")
    try:
        input("Pressione [ENTER] para fechar o túnel...")
    finally:
        close_ssh_tunnel()
        print("\nTúnel SSH fechado!")
    # convert_publication_dates()