call venv\Scripts\activate
python -m horopter.load_articles
python -m horopter.analyze_articles
python -m horopter.aggregate
python -m horopter.drop_old_records
PAUSE