"""Simple script to print number of rows in `practic2`.

Run from project root (PowerShell):

    python scripts/check_practic_count.py

It will create the Flask app (using `run.py`) and print the count or any DB error.
"""
import sys
from importlib import import_module

try:
    run = import_module('run')
except Exception as e:
    print('Failed to import run.py:', e)
    sys.exit(2)

app = run.create_app()

with app.app_context():
    db = __import__('flask').current_app.extensions['sqlalchemy']
    try:
        q = db.text('SELECT COUNT(*) FROM practic2')
        cnt = db.session.execute(q).scalar()
        print('practic2 rows:', cnt)
    except Exception as e:
        print('DB error:', e)
        try:
            db.session.rollback()
        except Exception:
            pass
        sys.exit(3)
