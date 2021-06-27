import requests
from fake_useragent import UserAgent
from pymongo import MongoClient
from pymongo.errors import DocumentTooLarge

HEADER = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-GB,en-US,en',
    'Dnt': '1',
    'Host': 'httpbin.org',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/83.0.4103.97 Safari/537.36',
    'X-Amzn-Trace-Id': 'Root=1-5ee7bbec-779382315873aa33227a5df6'}


class DocumentRetriever:

    def __init__(self, database: MongoClient):
        self.data = []
        self.database = database

    def retrieve_documents_from_vertical_webpages(self):
        request_header = {'User-Agent': str(UserAgent().chrome)}
        verticals = self.database['verticals'].find()
        vertical_documents = self.database['vertical-documents']
        for vertical in verticals:
            vertical_name = vertical['vertical_name']
            websites = self.database['vertical-websites'].find({'vertical_name': vertical_name})
            for i, website in enumerate(websites):
                if vertical_documents.count_documents(
                        {'vertical_name': vertical_name, 'website': website['website']}) < 1:
                    try:
                        response = requests.get(website['website'], headers=request_header, timeout=2)
                        if response.status_code == 200:
                            processed_document = {'vertical_name': vertical_name, 'html': response.text,
                                                  'website': website['website']}
                            try:
                                vertical_documents.insert_one(processed_document)
                            except DocumentTooLarge:
                                print('Processing', i, 'for', vertical_name, 'failed, document too large')
                        else:
                            print('Processing', i, 'for', vertical_name, 'failed, response code', response.status_code)
                    except requests.exceptions.Timeout:
                        print('Processing', i, 'for', vertical_name, 'failed, timed out after 2 seconds')
                    except requests.exceptions.SSLError:
                        print('Processing', i, 'for', vertical_name, 'failed, SSL error occurred')
                    except requests.exceptions.ContentDecodingError:
                        print('Processing', i, 'for', vertical_name, 'failed, did not receive text')
                    except requests.exceptions.TooManyRedirects:
                        print('Processing', i, 'for', vertical_name, 'failed, too many redirects')
                    except requests.exceptions.ConnectionError:
                        print('Processing', i, 'for', vertical_name, 'failed, connection error')
                    except ConnectionResetError:
                        print('Processing', i, 'for', vertical_name, 'failed, connection reset')

    def retrieve_documents_from_query_webpages(self):
        request_header = {'User-Agent': str(UserAgent().chrome)}
        queries = self.database['queries'].find()
        query_documents = self.database['query-documents']
        for query in queries:
            query_term = query['query']
            websites = self.database['query-websites'].find({'query': query_term})
            for i, website in enumerate(websites):
                if query_documents.count_documents({'query': query_term, 'website': website['website']}) < 1:
                    try:
                        response = requests.get(website['website'], headers=request_header, timeout=2)
                        if response.status_code == 200:
                            processed_document = {'query': query_term, 'html': response.text,
                                                  'website': website['website']}
                            try:
                                query_documents.insert_one(processed_document)
                            except DocumentTooLarge:
                                print('Processing', i, 'for', query_term, 'failed, document too large')
                        else:
                            print('Processing', i, 'for', query_term, 'failed, response code', response.status_code)
                    except requests.exceptions.Timeout:
                        print('Processing', i, 'for', query_term, 'failed, timed out after 2 seconds')
                    except requests.exceptions.SSLError:
                        print('Processing', i, 'for', query_term, 'failed, SSL error occurred')
                    except requests.exceptions.ContentDecodingError:
                        print('Processing', i, 'for', query_term, 'failed, did not receive text')
                    except requests.exceptions.TooManyRedirects:
                        print('Processing', i, 'for', query_term, 'failed, too many redirects')
                    except requests.exceptions.ConnectionError:
                        print('Processing', i, 'for', query_term, 'failed, connection error')
