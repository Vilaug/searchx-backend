from pymongo import MongoClient

from models.DocumentPreprocessor import DocumentPreprocessor
from models.DocumentRetriever import DocumentRetriever
from models.LabelMetaDocuments import label_meta_documents
from models.VerticalSelectionPipeline import VerticalSelectionPipeline

db = MongoClient('mongodb://localhost')['aggregated-search']

PREPROCESSED = "preprocessed"
VERTICAL_WEBSITES = "retrieved_vertical_websites"
QUERY_WEBSITES = "retrieved_query_websites"
IMPORTED_VERTICALS = "imported_verticals"
IMPORTED_QUERIES = "imported_queries"
VERTICAL_DOCUMENTS = "retrieved_vertical_documents"
QUERY_DOCUMENTS = "retrieved_query_documents"
META_LABELED = "meta_labeled_documents"


def main():
    config_collection = db['config']
    config = config_collection.find_one()
    config_filter = {'_id': config['_id']}

    document_retriever = DocumentRetriever(db)
    if not config.get(IMPORTED_QUERIES) or not config.get(IMPORTED_VERTICALS) or not config.get(
            VERTICAL_WEBSITES) or not config.get(QUERY_WEBSITES):
        print('Verticals or Queries are not imported or their websites not retrieved.')
        print('please run the backend initialization script')
        return

    if not config.get(VERTICAL_DOCUMENTS):
        document_retriever.retrieve_documents_from_vertical_webpages()
        config_collection.update_one(config_filter, {'$set': {VERTICAL_DOCUMENTS: True}})
    print('Vertical documents are retrieved')

    if not config.get(QUERY_DOCUMENTS):
        document_retriever.retrieve_documents_from_query_webpages()
        config_collection.update_one(config_filter, {'$set': {QUERY_DOCUMENTS: True}})
    print('Query documents are retrieved')

    if not config.get(META_LABELED):
        label_meta_documents(db)
        config_collection.update_one(config_filter, {'$set': {META_LABELED: True}})
    print('Meta documents are labeled')

    if not config.get(PREPROCESSED):
        DocumentPreprocessor(db).preprocess_documents()
        config_collection.update_one(config_filter, {'$set': {PREPROCESSED: True}})
    print('Documents are preprocessed into training/evaluating data')

    pipeline = VerticalSelectionPipeline(db)
    pipeline.evaluate()


if __name__ == "__main__":
    main()
