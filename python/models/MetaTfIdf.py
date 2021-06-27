from sklearn.base import BaseEstimator
from sklearn.feature_extraction.text import TfidfVectorizer


class MetaTfIdf(BaseEstimator):

    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer()

    def fit(self, df_x, df_y=None):
        df_x1 = map(lambda x: x[1], df_x)
        self.tfidf_vectorizer.fit(df_x1)
        return self

    def transform(self, df_x):
        df_x1 = map(lambda x: x[1], df_x)
        return self.tfidf_vectorizer.transform(df_x1)
