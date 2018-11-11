import logging
import itertools
import requests
import hashlib
import time
from bs4 import BeautifulSoup
from .helpers import generate_strings_by_template, unpack_template, flatten_list



class Parser:
    pass



class VkParser(Parser):
    def __init__(parser_task, token):
        pass



class PaginatedSiteParser(Parser):
    def __init__(self, parser_task):
        self.source = parser_task['source']
        self.base_url = parser_task['base_url']
        self.task_city_id = parser_task['city_id']
        try:
            #parse params
            self.title_markup = parser_task['parse_params']['title_markup']
            self.text_markup = parser_task['parse_params']['text_markup']
            self.url_markup = parser_task['parse_params'].get('url_markup', None)
            self.url_keys = {}
            #fetch params
            for key in unpack_template(self.base_url):
                self.url_keys[key] = parser_task['fetch_params'][key]
            self.sleep = parser_task['fetch_params'].get('sleep', 0)
            self.urls = generate_strings_by_template(self.base_url, self.url_keys)
            #status
            self.status = 'ready'
        except KeyError as e:
            logging.error('parser parameter missing: %s', e)
            self.status = 'missing params'
        logging.info(' '.join([str(self), self.status]))
        
    
    def __str__(self):
        return "Parser for {}".format(self.source)
    
    
    def fetch_page(self, url):
        time.sleep(self.sleep)
        logging.info('Fetching {}'.format(url))
        return {'html': requests.get(url).text, 'url': url}
    
    
    def parse_page(self, raw_page):
        soup = BeautifulSoup(raw_page['html'], "html.parser")
        titles = soup.select(self.title_markup)
        texts = soup.select(self.text_markup)
        article_urls = soup.select(self.url_markup) \
                       if self.url_markup else [None for t in texts] 
        if len(texts) == len(titles) == len(article_urls):
            return [{'title': i[0].text, 
                     'text': i[1].text, 
                     'url': i[2].get('href') if i[2] else raw_page['url'],
                     'hashed': hashlib.sha1((i[0].text+i[1].text).encode('utf-8')).hexdigest()} 
                    for i in list(zip(titles, texts, article_urls))] 
        error_msg = "Unequal number of elements found: {} texts, {} titles, {} urls"
        logging.error(error_msg.format(len(texts), len(titles), len(article_urls)))
        return []
        
    
    def run_parser(self):
        raw_pages = [self.fetch_page(url) for url in self.urls]
        parsed_pages = [self.parse_page(page) for page in raw_pages]
        return flatten_list(parsed_pages)

    
    def complete_task(self):
        if self.status != "ready":
            logging.error('Parser stopped due to being not ready')
            return []
        articles = self.run_parser()
        parsing_result = []
        for article in articles: 
            parsing_info = {'timestamp': int(time.time()),
                            'city_id': self.task_city_id,
                            'source': self.source,
                            'meta': {'parser': str(self)}}
            article_result = {**article, **parsing_info}
            parsing_result.append(article_result)
        return parsing_result



parser_map = {
    'PaginatedSiteParser': PaginatedSiteParser 
}