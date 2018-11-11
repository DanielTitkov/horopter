from .database import Session, Article
from .utils.helpers import get_timestamps
import datetime
import configparser

import sys
sys.path.append('../')
import config

import logging

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', 
                    level=logging.INFO, datefmt='%I:%M:%S')


if __name__ == '__main__':
    config = config.Config
    to_ts, _ = get_timestamps(int(config.ARTICLE_LIFETIME))

    logging.info('Deleting records ealier than {}'.format(
        datetime.datetime.fromtimestamp(to_ts).isoformat()))

    session = Session()
    records_to_drop = session.query(Article.id).\
                      filter(Article.timestamp < to_ts).\
                      subquery()

    n_deleted = session.query(Article).\
                filter(Article.id.in_(records_to_drop)).\
                delete(synchronize_session='fetch')
            
    session.commit()
    session.close()

    logging.info('{} records droped'.format(n_deleted))
