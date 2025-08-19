# COMLProcessing

## Setup

Sistema de Análise e Extração de Dados sobre Criminalidade

Este projeto implementa um pipeline de Processamento de Linguagem Natural (PLN) para analisar notícias sobre criminalidade. O sistema é capaz de classificar a relevância dos artigos e extrair informações estruturadas de textos pertinentes, utilizando modelos de Machine Learning e um Modelo de Linguagem Amplo (LLM) para a extração de dados detalhados.🚀 Funcionalidades PrincipaisConexão Segura com Banco de Dados: Utiliza um túnel SSH para se conectar de forma segura a um banco de dados MongoDB, onde as notícias são armazenadas.Classificação de Relevância: Emprega pipelines de Machine Learning (scikit-learn) para classificar automaticamente se uma notícia é relevante para o tema de crime organizado.Avaliação de Modelos: Compara diferentes técnicas de vetorização, como TF-IDF e Doc2Vec, para encontrar o modelo de classificação com melhor desempenho. Os resultados são registrados para análise.Extração de Entidades com LLM: Usa um LLM (via Ollama) para extrair informações detalhadas de notícias relevantes, como:Nomes de organizações criminosasLocalização (país, estado, município)Datas dos eventosOcorrência de conflitosApreensão de drogas e armas (incluindo tipos e quantidades)Atores envolvidos e suas relações.Saída Estruturada: Salva os dados extraídos em um formato limpo e estruturado (arquivo .csv), pronto para análise e visualização.

🛠️ Tecnologias Utilizadas
Linguagem: Python 3
Banco de Dados: MongoDB
Machine Learning: scikit-learn, gensim, imbalanced-learn
LLM & PLN: langchain, ollama
Utilitários: PyYAML, tqdm, pandas

⚙️ Configuração do AmbienteSiga os passos abaixo para configurar o ambiente de desenvolvimento.Pré-requisitosPython 3.8 ou superiorAcesso a uma instância MongoDBOllama instalado e com um modelo LLM disponível (ex: brunoconterato/Gemma-3-Gaia-PT-BR-4b-it)

1. Clonar o Repositóriogit clone <URL_DO_SEU_REPOSITORIO>
cd <NOME_DO_PROJETO>
2. Criar e Ativar Ambiente Virtual 
É altamente recomendado usar um ambiente virtual para isolar as dependências do projeto.# Criar o ambiente
python -m venv .venv

# Ativar no Linux/macOS
source .venv/bin/activate

# Ativar no Windows
.venv\Scripts\activate
3. Instalar DependênciasInstale todas as bibliotecas necessárias com um único comando:pip install -r requirements.txt
4. Configurar CredenciaisCrie um arquivo config.yml na raiz do projeto. Este arquivo não deve ser enviado para o controle de versão (já está no .gitignore). Preencha com suas credenciais:# Exemplo de config.yml
lamcad:
    server_ip: "SEU_IP_DE_SERVIDOR"
    server_port: 22
    ssh_username: "SEU_USUARIO_SSH"
    ssh_password: "SUA_SENHA_SSH"
    # ... outras configurações de bind ...

mongodb_lamcad:
    uri: "SUA_URI_MONGODB"
    database: "NOME_DO_BANCO"
    # ... outras configurações de coleção ...
▶️ Como ExecutarPara iniciar o pipeline completo de busca, classificação e extração, execute o script main.py:python main.py
O script irá:Conectar-se ao banco de dados.Buscar notícias relevantes.Iterar sobre cada notícia, usando o LLM para extrair as características definidas em prompt.py.Exibir uma barra de progresso durante a extração.Salvar os resultados no arquivo caracteristicas_extraidas_ollama.csv.📂 Estrutura do Projeto.
├── data/
│   ├── database.py         # Funções para interagir com o MongoDB via túnel SSH.
│   └── preprocessing.py    # Scripts para preparar os dados para os modelos.
├── evaluation/
│   └── evaluation.py       # Lógica para avaliar e comparar os pipelines de ML.
├── models/
│   ├── pipelines.py        # Definição dos pipelines de classificação (TF-IDF, Doc2Vec).
│   └── vectorizers.py      # Wrapper customizado do Doc2Vec para compatibilidade com scikit-learn.
├── .gitignore              # Arquivos a serem ignorados pelo Git.
├── main.py                 # Ponto de entrada principal do projeto.
├── prompt.py               # Define a estrutura de dados (Pydantic) e o template do prompt para o LLM.
├── requirements.txt        # Lista de todas as dependências Python.
└── README.md               # Esta documentação.
