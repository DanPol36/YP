"""Dump first N rows from `practic2` to help debug empty clients page.

Run from project root:
    python scripts/dump_practic_samples.py

This prints selected columns and helps verify column names/values.
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
        q = db.text(
            'SELECT id, "ФИО", COALESCE("Номер_телефона", "") AS phone, "Почта" FROM practic2 LIMIT 20'
        )
        rows = db.session.execute(q).mappings().fetchall()
        if not rows:
            print('No rows returned from practic2')
        else:
            for r in rows:
                print(dict(r))
    except Exception as e:
        print('DB error:', e)
        try:
            db.session.rollback()
        except Exception:
            pass
        sys.exit(3)
