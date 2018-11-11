import os

class Config:
	PARSING_FREQ = 604800 / 2
	PARSER_PROCESSES = 1
	AGGREGATE_SPAN = 604800
	ARTICLE_LIFETIME = 604800 * 2
	MAPBOX_ACCESS_TOKEN = os.environ.get('MAPBOX_ACCESS_TOKEN', None)
	DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///articles.db')
