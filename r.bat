git pull
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch horopter/alembic.ini" --prune-empty --tag-name-filter cat -- --all
git push
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch horopter\alembic.ini" --prune-empty --tag-name-filter cat -- --all
git push
git filter-branch --force --index-filter "git rm --cached --ignore-unmatch alembic.ini" --prune-empty --tag-name-filter cat -- --all
git push
PAUSE