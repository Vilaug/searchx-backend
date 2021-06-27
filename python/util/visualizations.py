import matplotlib.pyplot as plt
import seaborn as sns
from pymongo import MongoClient
from sklearn.manifold import TSNE
from sklearn.pipeline import Pipeline, FeatureUnion

from database.db import DB
from models.MetaTfIdf import MetaTfIdf
from models.TextTfIdf import TextTfIdf

db = DB(MongoClient('mongodb://localhost')['aggregated-search'])


def save_document_class_visualization():
    pipeline = Pipeline([('features', FeatureUnion([('text', TextTfIdf()), ('meta', MetaTfIdf())])), ('tsne', TSNE())])
    x = db.get_vertical_text_list()
    y = db.get_vertical_list()
    results = pipeline.fit_transform(x, y=y)
    data = dict()
    data['TSNE X'] = results[:, 0]
    data['TSNE Y'] = results[:, 1]
    data['y'] = y
    plt.figure(figsize=(10, 10))
    sns.scatterplot(
        x="TSNE X", y="TSNE Y",
        hue="y",
        data=data,
        legend="full",
    )
    plt.savefig("distribution.png")
    plt.show()


def save_document_class_distribution():
    vertical_documents = MongoClient('mongodb://localhost')['aggregated-search']['vertical-data'].aggregate([
        {
            '$group': {
                '_id': '$vertical_name',
                'count': {
                    '$sum': 1
                }
            }
        }
    ])
    names = []
    count = []
    for vertical_document in vertical_documents:
        names.append(vertical_document['_id'])
        if vertical_document['_id'] == "Jobs":
            print(vertical_document['count'])
        count.append(vertical_document['count'])
    plt.bar(names, count)
    plt.xticks(rotation='vertical')
    plt.tight_layout()
    plt.savefig('document_distribution.png')
    plt.show()


save_document_class_distribution()
