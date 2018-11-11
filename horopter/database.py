import psycopg2
import json
import logging
import time
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey, Column, String, JSON, BigInteger, Integer, DateTime
from sqlalchemy.orm import scoped_session, sessionmaker, relationship
from .parsing.helpers import flatten_list


import sys
sys.path.append('../')
import config

DATABASE_URI = config.Config.DATABASE_URI
engine = create_engine(DATABASE_URI, echo=False, client_encoding = 'utf8')
# pool_timeout=20, pool_recycle=299
Session = scoped_session(sessionmaker(bind=engine))
Base = declarative_base()


# def open(sqlite_db_path = None):
#     engine = create_engine('sqlite:///' + 'articles.db')
#     session_factory = sessionmaker(bind=engine)
#     return scoped_session(session_factory)()


def get_timestamp():
    return int(time.time())
    


class Article(Base):
    __tablename__ = 'articles'
    
    id = Column(Integer, primary_key=True)
    city_id = Column(String(20), ForeignKey('cities.city_id'))
    hashed = Column(String(50), unique = True)
    source = Column(String(200))
    text = Column(String(2000))
    title = Column(String(1000))
    url = Column(String(1000))
    timestamp = Column(BigInteger)
    meta = Column(String(200)) #maybe change to json on other db
    analysis = Column(String(200)) #maybe change to json on other db
        
    city = relationship("City", back_populates="articles")
    

    def __repr__(self):
        return "<Article({})>".format(self.title[:200])


    @staticmethod
    def save_articles_to_db(session, articles=[]):
        for article in articles:
            session.add(Article(
                city_id=article['city_id'], 
                hashed=article['hashed'], 
                source=article['source'], 
                text=article['text'],
                title=article['title'], 
                url=article['url'], 
                timestamp=article['timestamp'], 
                meta=json.dumps(article['meta']))
            )
        session.commit()


    
class City(Base):
    __tablename__ = 'cities'
    
    id = Column(Integer, primary_key=True)
    city_name = Column(String(30))
    city_id = Column(String(20), unique = True)
    coordinates = Column(String(30))
    
    articles = relationship("Article", back_populates="city")
    tasks = relationship("Task", back_populates="city")
    results = relationship("Result", back_populates="city")
    
    def __repr__(self):
        return "<City({}:{})>".format(self.city_name, self.city_id)
   


class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    city_id = Column(String(20), ForeignKey('cities.city_id'))
    source = Column(String(200))
    parser = Column(String(50))
    base_url = Column(String(2000))
    fetch_params = Column(String(500))
    parse_params = Column(String(500))
    clean_params = Column(String(500))
    status = Column(String(20), default="ACTIVE")

    city = relationship("City", back_populates="tasks")


    def __repr__(self):
        return "<Run parser {} on {})>".format(self.parser, self.source)


    @staticmethod
    def prepare_tasks_from_db(session):
        parser_tasks = []
        for task in session.query(Task).filter(Task.status == "ACTIVE").all():
            parser_task = {
                'parser': task.parser, 
                'task': {
                    'source': task.source,
                    'base_url': task.base_url,
                    'city_id': task.city_id,
                    'parse_params': json.loads(task.parse_params),
                    'fetch_params': json.loads(task.fetch_params),
                    'clean_params': json.loads(task.clean_params)
                }
            }
            parser_tasks.append(parser_task)
        logging.info('{} parser tasks prepared'.format(len(parser_tasks)))
        return parser_tasks



class Result(Base):
    __tablename__ = 'results'

    id = Column(Integer, primary_key=True)
    city_id = Column(String(20), ForeignKey('cities.city_id'))
    timestamp = Column(BigInteger, default=get_timestamp)
    summary = Column(String(500)) #maybe change to json on other db

    city = relationship("City", back_populates="results")


    def __repr__(self):
        return "<Result from city {} at {})>".format(self.city_id, self.timestamp)



def get_unsaved_objects(session, model, key, objects=[]):
    new_objects = [obj[key] for obj in objects]
    previously_saved_objects = session.query(getattr(model, key))\
                               .filter(getattr(model, key).in_(new_objects)).all()
    return [obj for obj in objects 
            if obj[key] not in set(flatten_list(previously_saved_objects))]


Base.metadata.create_all(engine)