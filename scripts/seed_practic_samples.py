"""Seed a few sample clients into `practic2` for local development.

Run from project root (PowerShell):

    python scripts/seed_practic_samples.py

This will insert sample rows only if `practic2` is empty. It uses the app
factory `create_app()` from `run.py` so it respects your DB config.
"""
import sys
from importlib import import_module

try:
    run = import_module('run')
except Exception as e:
    print('Failed to import run.py:', e)
    sys.exit(2)

app = run.create_app()

SAMPLES = [
    {
        'ФИО': 'Иванов Иван Иванович',
        'Пол': 'Мужской',
        'Адрес': 'г. Москва, ул. Ленина, 1',
        'Возраст': 34,
        'Дата_рождения': None,
        'Номер_телефона': '+7 (900) 111-22-33',
        'Почта': 'ivanov@example.com',
        'Примечания': 'Тестовый клиент'
    },
    {
        'ФИО': 'Петрова Мария Сергеевна',
        'Пол': 'Женский',
        'Адрес': 'г. Санкт-Петербург, Невский пр., 10',
        'Возраст': 28,
        'Дата_рождения': None,
        'Номер_телефона': '+7 (911) 222-33-44',
        'Почта': 'm.petrov@example.com',
        'Примечания': 'Тестовый клиент 2'
    },
    {
        'ФИО': 'Сидоров Алексей Павлович',
        'Пол': 'Мужской',
        'Адрес': 'г. Казань, ул. Кремлёвская, 5',
        'Возраст': 41,
        'Дата_рождения': None,
        'Номер_телефона': '+7 (922) 333-44-55',
        'Почта': 'a.sidorov@example.com',
        'Примечания': 'Тестовый клиент 3'
    }
]

with app.app_context():
    from flask import current_app
    db = current_app.extensions['sqlalchemy']
    try:
        cnt = db.session.execute(db.text('SELECT COUNT(*) FROM practic2')).scalar()
    except Exception as e:
        print('DB error while counting practic2:', e)
        try:
            db.session.rollback()
        except Exception:
            pass
        sys.exit(3)

    if cnt and int(cnt) > 0:
        print('practic2 already has', cnt, 'rows — skipping seeding.')
        sys.exit(0)

    print('practic2 is empty, inserting sample rows...')
    sql = db.text('''
        INSERT INTO practic2 (
            "ФИО", "Пол", "Адрес", "Возраст", "Дата_рождения", "Номер_телефона", "Почта", "Примечания"
        ) VALUES (
            :fio, :gender, :address, :age, :birth_date, :phone, :email, :notes
        )
    ''')

    try:
        for s in SAMPLES:
            db.session.execute(sql, {
                'fio': s['ФИО'],
                'gender': s['Пол'],
                'address': s['Адрес'],
                'age': s['Возраст'],
                'birth_date': s['Дата_рождения'],
                'phone': s['Номер_телефона'],
                'email': s['Почта'],
                'notes': s['Примечания']
            })
        db.session.commit()
        print('Inserted', len(SAMPLES), 'sample clients.')
    except Exception as e:
        print('Failed to insert samples:', e)
        try:
            db.session.rollback()
        except Exception:
            pass
        sys.exit(4)

    # show samples
    try:
        rows = db.session.execute(db.text('SELECT id, "ФИО", COALESCE("Номер_телефона", '') AS phone, "Почта" FROM practic2')).mappings().fetchall()
        for r in rows:
            print(dict(r))
    except Exception as e:
        print('Error fetching inserted rows:', e)
        try:
            db.session.rollback()
        except Exception:
            pass
        sys.exit(5)
