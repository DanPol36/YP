"""List tables in the configured DATABASE_URL and check for `practic2` and `order2`.

Run from project root:
    python scripts/list_tables.py

This prints table names and helps verify that legacy tables exist in the active DB.
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
    from flask import current_app
    db = current_app.extensions['sqlalchemy']
    try:
        res = db.session.execute(db.text("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")).fetchall()
        tables = [r[0] for r in res]
        print('Tables in public schema:')
        for t in tables:
            print(' -', t)
        print('\npractic2 present:', 'practic2' in tables)
        print('order2 present:', 'order2' in tables)
    except Exception as e:
        print('DB error while listing tables:', e)
        try:
            db.session.rollback()
        except Exception:
            pass
        sys.exit(3)
