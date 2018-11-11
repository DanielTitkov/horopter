from .parsing.parsers import PaginatedSiteParser, parser_map
from .parsing.cleaners import TextCleaner
from .database import Session, Article, Task
from .database import get_unsaved_objects

import sys
sys.path.append('../')
import config

from functools import partial
import multiprocessing
import random
import logging
import pprint
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(threadName)s - %(message)s', 
                    level=logging.INFO, 
                    datefmt='%I:%M:%S')


def prepare_articles(task, parser_map):
    parser_output = parser_map[task['parser']](task['task']).complete_task()
    cleaner = TextCleaner(task['task']['clean_params'])
    for article in parser_output:
        article['text'] = cleaner.complete_task(article['text'])
        article['title'] = cleaner.complete_task(article['title'])
    return parser_output


def resolve_task(task, parser_map, verbose=False):
    session = Session()
    logging.info('started {}'.format(task['task']['source']))
    prepared_articles = prepare_articles(task, parser_map)
    articles_to_save = get_unsaved_objects(
        session=session, 
        model=Article, 
        key='hashed', 
        objects=prepared_articles
    )
    Article.save_articles_to_db(session, articles_to_save)
    logging.info('got {} articles'.format(len(prepared_articles)))
    logging.info('{} new articles saved in DB'.format(len(articles_to_save)))
    logging.info('done {}'.format(task['task']['source']))
    if verbose:
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(prepared_articles)
    session.close()

    
    
if __name__ == '__main__':
    parser_tasks = Task.prepare_tasks_from_db(session=Session())
    random.shuffle(parser_tasks)
    with multiprocessing.Pool(config.Config.PARSER_PROCESSES) as pool:
        pool.map(partial(resolve_task, parser_map=parser_map), parser_tasks)
        logging.info('Completed {} tasks'.format(len(parser_tasks)))