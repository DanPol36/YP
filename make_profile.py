# make_profile.py
import cProfile
from app import create_app
import os

app = create_app()

# Если нужен контекст приложения (например, DB), можно открыть app.app_context()
with app.app_context():
    with cProfile.Profile() as pr:
        with app.test_client() as client:
            # если требуется логин:
            client.post('/login', data={'username':'admin', 'password':'12345'})
            # пример запросов для профилирования:
            client.get('/clients/')
            client.get('/clients/create')   
            # если нужно отправить POST (создать тестовую запись):
            client.post('/clients/create', data={
                'fio': 'Тест Тестов',
                'gender': 'M',
                'age': '30',
                'birth_date': '1995-01-01',
                'phone': '+70000000000',
                'email': 't@test.local',
                'address': 'ул Тестовая',
                'notes': 'тест'
            })

    pr.dump_stats('profile.prof')
    print("Готово! Файл profile.prof создан")