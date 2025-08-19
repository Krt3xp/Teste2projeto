from imblearn.under_sampling import RandomUnderSampler
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.pipeline import Pipeline

from models.vectorizers import Doc2VecTransformer

pipelines = {
    '1': Pipeline([
        ('tf-idf', TfidfVectorizer(strip_accents='unicode', min_df=10, ngram_range=(1, 2), max_features=1500)),
        ('extra-trees-classifier', ExtraTreesClassifier(random_state=0))]),
    '2': Pipeline([
        ('tf-idf', TfidfVectorizer(strip_accents='unicode', min_df=10, ngram_range=(1, 2))),
        ('extra-trees-classifier', ExtraTreesClassifier(random_state=0))]),
    '3': Pipeline([
        ('doc2vec', Doc2VecTransformer(min_count=15, epochs=40, vector_size=75)),
        ('log-reg', LogisticRegression(random_state=0))
    ])
}

# Filtro de pipelines que utilizam TF-IDF
tf_idf_pipelines = {}
for pipeline_id, pipeline in pipelines.items():
    if 'tf-idf' in pipeline.named_steps.keys():
        tf_idf_pipelines[pipeline_id] = pipeline
