# COMLProcessing

## Setup

(Preferencialmente em um ambiente virtual)

1. Geração do clone deste repositório com o comando:
    ```shell
    git clone https://gitlab.com/ivato/textanalysis/crimeorganizado/comlprocessing.git
    ```

2. Acesso ao projeto:
    ```shell
    cd cowebscraping
    ```

3. Criação e inicialização do ambiente virtual:
    ```shell
    virtualenv .venv
    source .venv/bin/activate
    ```

4. Instalação dos pacotes necessários:
    ```shell
    pip install -r requirements.txt
    ```

5. Especificação das credenciais de acesso ao banco de dados em um arquivo intitulado `config.yaml` e no seguinte formato:
    ```yml
    lamcad:
        server_ip: "<value>"
        server_port: <value>
        ssh_username: "<value>"
        ssh_password: "<value>"
        local_bind_ip: "<value>"
        local_bind_port: <value>
        remote_bind_ip: "<value>"
        remote_bind_port: <value>

    mongodb_lamcad:
        uri: "<value>"
        database: "<value>"
        accepted_news_collection: "<value>"
        unaccepted_news_collection: "<value>"
    ```

## Execução

Ao executar o script `main.py` (com python `main.py`), os pipelines de classificação serão executados sob as notícias já classificadas manualmente e os resultados serão armazenados no banco de dados MongoDB (na coleção `classification_pipelines`). Em seguida, o pipeline com o melhor score será utilizado para classificar todas as notícias no banco.