from sklearn.base import BaseEstimator, TransformerMixin
from gensim.models.doc2vec import Doc2Vec, TaggedDocument

# Scikit-Learn não possui suporte a Doc2Vec, então envelopamos o Doc2Vec
# do Gensim em um formato suportado pelo Scikit-Learn
class Doc2VecTransformer(BaseEstimator, TransformerMixin):
    def __init__(self, vector_size=100, window=5, min_count=2, workers=4, epochs=10):
        self.vector_size = vector_size
        self.window = window
        self.min_count = min_count
        self.workers = workers
        self.epochs = epochs
        self.model = None

    def fit(self, documents, y=None):
        # Prepares data as TaggedDocument
        tagged_documents = [TaggedDocument(doc.split(), [i]) for i, doc in enumerate(documents)]

        # Initialize and build the model
        self.model = Doc2Vec(
            vector_size=self.vector_size,
            window=self.window,
            min_count=self.min_count,
            workers=self.workers
        )
        self.model.build_vocab(tagged_documents)

        # Train the model
        self.model.train(tagged_documents, total_examples=len(tagged_documents), epochs=self.epochs)
        return self

    def transform(self, documents):
        # Convert documents to vectors
        vectors = [self.model.infer_vector(doc.split()) for doc in documents]
        return vectors

    def fit_transform(self, documents, y=None):
        self.fit(documents, y)
        return self.transform(documents)