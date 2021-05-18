import json
import re

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from pymongo import MongoClient

from models.cli_parser import get_training_data_cli_parser

args = get_training_data_cli_parser().parse_args()

db_client = MongoClient('localhost:27017')
db = db_client.get_database('aggregated-search')


def main():
    config_collection = db['config']
    config = config_collection.find_one()
    config_filter = {'_id': config['_id']}
    if config is None:
        config = {
            "have_preprocessed": False,
            "have_retrieved_websites": False,
            "have_preprocessed_websites": True}
        db['config'].insert_one(config)
    if not config.get('have_imported_verticals'):
        load_verticals()
        config_collection.update_one(config_filter, {'$set': {'have_imported_verticals': True}})

    if not config.get('have_retrieved_websites'):
        parse_websites_to_db()
        config_collection.update_one(config_filter, {'$set': {'have_retrieved_websites': True}})

    if not config.get('have_preprocessed'):
        retrieve_text_from_webpages()
        config_collection.update_one(config_filter, {'$set': {'have_preprocessed': True}})


def read_json(filename):
    with open('../../data/' + filename + '.json', encoding="utf8") as f:
        content = f.read()
        dictionary = json.loads(content)
        return dictionary


def retrieve_text_from_webpages():
    request_header = {'User-Agent': str(UserAgent().chrome)}
    verticals = db['verticals'].find()
    processed = db['processed']
    regex = re.compile(r"\s+")
    for vertical in verticals:
        websites = db['websites'].find({'vertical_name': vertical['name']})
        for i, website in enumerate(websites):
            if processed.count_documents({'vertical_name': vertical['name'], 'url': website['url']}) < 1:
                try:
                    response = requests.get(website['url'], headers=request_header, timeout=1)
                    if response.status_code == 200:
                        response_only_text = BeautifulSoup(response.text, 'lxml').text
                        response_only_text = regex.sub(" ", response_only_text).strip()
                        processed_document = {'vertical_name': vertical['name'], 'text': response_only_text,
                                              'url': website['url']}
                        processed.insert_one(processed_document)
                    else:
                        print('Processing', i, 'failed, response code', response.status_code)
                except requests.exceptions.Timeout:
                    print('Processing', i, 'failed, timed out after 1 second')
                except requests.exceptions.SSLError:
                    print('Processing', i, 'failed, SSL error occurred')
                except requests.exceptions.ContentDecodingError:
                    print('Processing', i, 'failed, did not receive text')


def parse_websites_to_db():
    collection = db['websites']
    labeled_websites = read_json('vertical_websites')
    for vertical, websites in labeled_websites.items():
        for website in websites:
            if collection.count_documents({'vertical_name': vertical, 'url': website['url']}) < 1:
                website['vertical_name'] = vertical
                collection.insert_one(website)


def load_verticals():
    collection = db['verticals']
    with open('../../data/verticals_fedweb2014.txt') as f:
        lines = f.readlines()
        if len(lines) > collection.estimated_document_count():
            for line in lines:
                vertical = {}
                label_name = line.split()
                if '/' in label_name[1]:
                    label_name[1] = label_name[1].split('/')[1]
                vertical['label'] = label_name[0]
                vertical['name'] = label_name[1]
                collection.insert_one(vertical)


if __name__ == "__main__":
    main()

#
# SEARCH_URL = 'http://odp.org/search/'
#
# ARGUMENTS = {
#     'c2coff': 1,
#     'cr': 'countryUS',
#     'filter': 1,
#     'gl': 'us',
#     'lr': 'lang_en',
#     'cx': '4fcb9c7533d2c5c2f'
# }
#
# def get_request_url():
#     url = SEARCH_URL
#     for option, value in ARGUMENTS.items():
#         url += '&' + option + '=' + str(value)
#     return url

#     vertical_websites = {}
#     request_url = get_request_url()
#     for label, name in labeled_verticals.items():
#         vertical_url = request_url + '&q=' + name
#         website_urls = []
#         for i in range(10):
#             current_vertical_url = vertical_url + '&start=' + str(i * 10 + 1)
#             print(current_vertical_url)
#             response = requests.get(current_vertical_url)
#             while response.status_code != 200
#                 if response.status_code == 200:
#                     result = json.loads(response.content)
#
#                     while
#                         if result:
#                             for item in result.get('items'):
#                                 website_urls.append(item.get('link'))
#                         else:
#
#         vertical_websites[name] = website_urls
#
#     return vertical_websites


# def extract_urls_for_verticals(labeled_verticals, n):
#     headers = {
#         'User-Agent': 'PostmanRuntime/7.28.0',
#         'Accept': '*/*',
#         'Accept-Encoding': 'gzip, deflate, br',
#         'Connection': 'keep-alive',
#         'Content-Type': 'application/x-www-form-urlencoded'
#     }
#     cookies, token = get_token_and_cookie(headers)
#     collection = db['websites']
#     for label, vertical_name in labeled_verticals.items():
#         result = requests.post(SEARCH_URL, headers=headers, cookies=cookies, data={
#             'token': token,
#             'q': vertical_name
#         })
#         soup = BeautifulSoup(result.content, 'html.parser')
#         li_tags = soup.body.div.ul.find_all('li')
#         website_urls = []
#         print(len(li_tags))
#         for li in li_tags:
#             website_urls.append(li.h4.a['href'])
#         vertical_websites[vertical_name] = website_urls
#     return vertical_websites
#
#
# def get_token_and_cookie(headers):
#     result = requests.get(SEARCH_URL, headers=headers)
#     for line in result.content.splitlines():
#         if 'name="token"' in str(line):
#             token_part = str(line).split('value="')[1].split('"')[0]
#             return result.cookies, token_part
