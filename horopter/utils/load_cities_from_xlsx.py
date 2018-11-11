import pandas as pd
import logging
from ..database import Session, City
from ..database import get_unsaved_objects
import argparse

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(threadName)s - %(message)s', 
                    level=logging.INFO, 
                    datefmt='%I:%M:%S')

# crap code follows
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('xlsx', nargs='?', help='need city_id and city_name columns')
    args = parser.parse_args()

    logging.info('reading {}'.format(args.xlsx))

    session = Session()
    
    cities_df = pd.read_excel(args.xlsx)\
                .dropna()\
                .groupby('city_id', as_index=False)\
                .agg(lambda x: list(x)[0])
            
    cities = cities_df.to_dict('records')
    logging.info('read {} cities from file'.format(len(cities)))
    
    cities_chunks = [cities[i:i + 900] 
                     for i in range(0, len(cities), 900)]
    
    for chunk in cities_chunks:
        cities_to_save = get_unsaved_objects(session=session, 
                                               model=City, 
                                               key='city_id', 
                                               objects=chunk)
        for city in cities_to_save:
            session.add(City(city_id=city['city_id'], 
                             city_name=city['city_name'], 
                             coordinates=city['coordinates']))
        session.commit()
        
        logging.info('got {} new cities'.format(len(chunk)))
        logging.info('{} cities saved in DB'.format(len(cities_to_save)))

    session.close()