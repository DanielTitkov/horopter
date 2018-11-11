from .analysis.polarity import PolarityAnalyzer
from .database import Session, Article

import pymorphy2
import pickle
import logging
import json

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', 
                    level=logging.INFO, 
                    datefmt='%I:%M:%S')



def load_pkl(path):
    with open(path, 'rb') as f:
        return pickle.load(f)
    

def prepare_result(analyzers=[], articles=[]):
    result_list = []
    for article in articles:
        result = {'analysis': {}}
        result['id'] = article.id
        for analyzer in analyzers:
            text_data = ' '.join([article.title, article.text])
            label = analyzer['analyzer'].predict(text_data)
            result['analysis'][analyzer['label']] = label
            result['analysis'] = json.dumps(result['analysis'])
        result_list.append(result)
    return result_list


if __name__ == '__main__':
    logging.info('Loading models...')
    morph = pymorphy2.MorphAnalyzer()
    pa = PolarityAnalyzer(load_pkl('pa_cl.pkl'), load_pkl('pa_vect.pkl'), morph=morph)
    analyzers = [{'analyzer': pa, 'label': 'polarity'},]
    logging.info('Analyzers ready')

    session = Session()
    articles = session.query(Article.id, 
                             Article.title, 
                             Article.text).filter(Article.analysis == None)
    logging.info('{} articles to analyze'.format(len(articles.all())))

    result = prepare_result(analyzers, articles)
    logging.info('Analysis is done')

    for row in result:
        session.query(Article).filter(Article.id == row['id']).update(row)
    session.commit()
    logging.info('Results saved in DB')
    session.close()