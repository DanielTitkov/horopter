from .database import Session, Article, Result
from .utils.helpers import get_timestamps

import sys
sys.path.append('../')
import config

from itertools import groupby
import time
import datetime
import json

import logging
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    level=logging.INFO, datefmt='%I:%M:%S')


def aggregate_dicts(dicts):
    result = {}
    for d in dicts:
        for k, v in d.items():
            if k in result:
                if v in result[k]:
                    result[k][v] += 1
                else:
                    result[k][v] = 1
            else:
                result[k] = {v: 1}
    return result


def group_and_aggregate(data, group_by, target, string_to_json=True):
    prep = json.loads if string_to_json else lambda x: x
    results = {}
    sorted_data = sorted(data, key=lambda x: getattr(x, group_by))
    for k, g in groupby(sorted_data, lambda x: getattr(x, group_by)):
        results[k] = aggregate_dicts(
            map(lambda x: prep(getattr(x, target)), g))
    return results


if __name__ == '__main__':
    config = config.Config
    from_ts, to_ts = get_timestamps(int(config.AGGREGATE_SPAN))
    logging.info('Aggregating from {} to {}'.format(
        datetime.datetime.fromtimestamp(from_ts).isoformat(),
        datetime.datetime.fromtimestamp(to_ts).isoformat()))

    session = Session()
    articles = session.query(Article).filter(
        Article.timestamp > from_ts,
        Article.timestamp < to_ts,
        Article.analysis != None).all()

    logging.info('{} articles to aggregate'.format(len(articles)))

    results = group_and_aggregate(articles, 'city_id', 'analysis')
    logging.info('Data on {} cities aggregated'.format(len(results)))

    result_objects = [Result(city_id=k, summary=json.dumps(v)) for k, v in results.items()]
    session.bulk_save_objects(result_objects)
    session.commit()
    session.close()

    logging.info('{} records saved to DB'.format(len(result_objects)))
