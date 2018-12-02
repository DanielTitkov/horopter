#!/bin/bash
# redirect stdout/stderr to a file
exec &> logfile.txt
cd horopter
echo ---------------------------------
date
source /home/ubuntu/horopter/venv/bin/activate
python -m horopter.load_articles
python -m horopter.analyze_articles
python -m horopter.aggregate
python -m horopter.drop_old_records
# python -m horopter.drop_old_records
# /home/ubuntu/horopter/horopter/analyze_articles.py
# ls | xargs -I {} echo "$(pwd -P)/{}" | xargs | sed 's/ /","/g'