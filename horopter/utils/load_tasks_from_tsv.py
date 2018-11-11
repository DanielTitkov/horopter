import pandas as pd
import logging
from horopter import database
import argparse

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(threadName)s - %(message)s', 
                    level=logging.INFO, 
                    datefmt='%I:%M:%S')

# crap code follows
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('tsv', nargs='?')
    parser.add_argument('backup', nargs='?')
    args = parser.parse_args()

    logging.info('reading {}'.format(args.tsv))
    logging.info('saving backup to {}'.format(args.backup))

    session = database.Session()

    # make backup
    task_keys = database.Task.__table__.columns.keys()
    query = [getattr(database.Task, k) for k in task_keys]
    backup = pd.DataFrame.from_records(session.query(*query).all(), columns=task_keys)
    backup.to_csv(args.backup, sep='\t', encoding='utf-8')

    #clear old tasks
    try:
        num_rows_deleted = session.query(database.Task).delete()
        logging.info('{} old tasks deleted from DB'.format(num_rows_deleted))
        session.commit()
    except Exception as e:
        logging.error(e)
        session.rollback()

    
        
    #upload new tasks
    tasks = pd.read_csv(args.tsv, sep='\t').to_dict('records')
    logging.info('read {} tasks from file'.format(len(tasks)))

    tasks_chunks = [tasks[i:i + 900] for i in range(0, len(tasks), 900)]
    for chunk in tasks_chunks:
        for task in chunk:
            session.add(database.Task(city_id=task['city_id'], 
                             source=task['source'], 
                             parser=task['parser'], 
                             base_url=task['base_url'], 
                             fetch_params=task['fetch_params'],
                             parse_params=task['parse_params'],
                             clean_params=task['clean_params']))
        session.commit()
        logging.info('{} tasks saved in DB'.format(len(chunk)))

    session.close()