from bs4 import BeautifulSoup


def label_meta_documents(db):
    label_documents(db['vertical-documents'])
    label_documents(db['query-documents'])


def label_documents(collection):
    ids = []
    for vertical_document in collection.find():
        soup = BeautifulSoup(vertical_document['html'], "lxml")
        for tag in soup.find_all("meta"):
            if tag.get("content", None) is not None:
                if tag.get("name", None) is not None:
                    if 'desc' in tag.get("name", None):
                        ids.append(vertical_document['_id'])
                        break
                if tag.get("property", None) is not None:
                    if 'desc' in tag.get("property", None):
                        ids.append(vertical_document['_id'])
                        break
    collection.update({'_id': {'$in': ids}}, {'$set': {"has_meta": True}}, multi=True)
    collection.update({'_id': {'$nin': ids}}, {'$set': {"has_meta": False}}, multi=True)
