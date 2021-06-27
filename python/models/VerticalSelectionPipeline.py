import json
import pickle
import subprocess
from collections import Counter

from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import FeatureUnion, Pipeline

from database.db import DB
from models.MetaTfIdf import MetaTfIdf
from models.TextTfIdf import TextTfIdf


class VerticalSelectionPipeline:

    def __init__(self, database):
        self.text_tfidf = TextTfIdf()
        self.meta_tfidf = MetaTfIdf()
        self.pipeline = None
        self.db = DB(database)

    def fit_pipeline(self):
        try:
            self.pipeline = pickle.load(open('model.dat', 'rb'))
        except (FileNotFoundError, EOFError):
            union = FeatureUnion([
                ("text_tfidf", self.text_tfidf),
                ("meta_tfidf", self.meta_tfidf)
            ])
            self.pipeline = Pipeline(steps=[
                ('features', union),
                ('classifier', RandomForestClassifier())])
            print('Started fitting')
            self.pipeline.fit(self.db.get_vertical_text_list(), y=self.db.get_vertical_list())
            print('Ended fitting')
            pickle.dump(self.pipeline, open('model.dat', 'wb'))

    def evaluate(self):
        self.fit_pipeline()
        print('Started predicting')
        f = open("../data/results.txt", "w")
        queries = self.db.get_queries()
        ruleset = json.load(open("../data/ruleset.json"))
        for i, query in enumerate(queries):
            found = False
            verticals = ['General']
            for vertical, keywords in ruleset.items():
                for word in query['query'].split():
                    for keyword in keywords:
                        if keyword == word:
                            verticals.append(vertical)
                            found = True
                            break
                    if found:
                        break

            query_texts = self.db.get_query_text_list(query['query'])
            predictions = self.pipeline.predict(query_texts)
            vertical_counter = Counter(predictions)
            most_common = vertical_counter.most_common()
            for prediction, count in most_common:
                if count / len(predictions) > 0.37 and prediction not in verticals:
                    verticals.append(prediction)
            for vertical in verticals:
                f.write(query['query_label'] + '\t ' + self.db.get_vertical_label(vertical) + '\t' + '1' + '\n')

        f.close()

        eval = subprocess.Popen(
            ["perl", "../data/evalVS.pl", '..\\data\\results.txt', '..\\data\\vertical-qrels.txt'],
            stdout=subprocess.PIPE)

        out = eval.communicate()[0]
        print(out.decode('utf-8'))
