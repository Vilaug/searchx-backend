import re

from bs4 import BeautifulSoup
from cleantext import clean


class DocumentPreprocessor:

    def __init__(self, db):
        self.db = db

    def preprocess_documents(self):
        self.preprocess_collection_documents("query-documents")
        self.preprocess_collection_documents("vertical-documents")

    def preprocess_collection_documents(self, collection):
        documents = self.db[collection].find()
        regex = re.compile(r"\s+")
        for document in documents:
            soup = BeautifulSoup(document['html'], "lxml")
            data_document = {
                "website": document['website']
            }
            if collection == "query-documents":
                data_document['query'] = document['query']
            else:
                data_document['vertical_name'] = document['vertical_name']

            for tag in soup.find_all("meta"):
                if tag.get("name", None):
                    if 'desc' in tag.get("name", None):
                        data_document['meta_description'] = tag.get("content", None)
                        break
                if tag.get("property", None):
                    if 'desc' in tag.get("property", None):
                        data_document['meta_description'] = tag.get("content", None)
                        break

            if not data_document.get('meta_description'):
                continue
            data_document['text'] = clean(regex.sub(" ", soup.text).strip(),
                                          to_ascii=True,  # transliterate to closest ASCII representation
                                          lower=True,  # lowercase text
                                          no_phone_numbers=True,  # replace all phone numbers with a special token
                                          no_numbers=True,  # replace all numbers with a special token
                                          no_digits=True,  # replace all digits with a special token
                                          no_punct=True,  # remove punctuations
                                          )
            self.db[collection.split('-')[0] + '-data'].insert(data_document)
