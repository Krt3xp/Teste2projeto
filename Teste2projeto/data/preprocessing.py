import random

def format_articles_for_prediction(relevant_articles: list[dict], non_relevant_articles: list[dict], balance=False) -> tuple[list[str], list[int]]:
    # Obtendo uma lista balanceada de notícias não relevantes
    if balance:
        non_relevant_articles = random.sample(non_relevant_articles, len(relevant_articles))

    # Colocando todos os textos das notícias em uma lista de sentenças
    sentences = [article['article'] for article in relevant_articles] + [article['article'] for article in non_relevant_articles]

    # Classificações reais das notícias balanceadas
    classifications = [1]*len(relevant_articles) + [0]*len(non_relevant_articles)

    return sentences, classifications