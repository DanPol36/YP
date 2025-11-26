Цель
Краткие и практичные инструкции для AI-агентов, чтобы быстро включиться в работу с этим репозиторием.

Быстрый запуск (development)
- Установить зависимости: `pip install -r requirements.txt`.
- Создать файл `.env` в корне и задать `DATABASE_URL` (обязательно) и при желании `SECRET_KEY`.
- Запустить приложение локально:
```
python run.py
```
Файл `run.py` при первом старте автоматически создаёт администратора: логин `admin`, пароль `12345`.

Архитектура — общая картина
- Фабрика приложения: функция `create_app()` в `app/__init__.py` — здесь настраиваются расширения и регистрируются blueprints.
- Blueprint'ы: `app/routes/auth.py`, `app/routes/documents.py`, `app/routes/people.py`.
- ORM: основные модели используют Flask-SQLAlchemy (`app/models/document.py`, `app/models/user.py`).
- Унаследованная таблица: `app/models/practic.py` использует отдельный `Base` из `instance/database.py` для маппинга таблицы `practic2` с русскоязычными именами колонок — это особый случай.
- Конфигурация БД: `instance/database.py` создаёт `engine` и `Base`. Flask-приложение использует `db = SQLAlchemy()` в `app/__init__.py`.
- Миграции: `flask_migrate.Migrate` инициализируется в `app/__init__.py`. Для миграций используйте `flask db` с переменной окружения `FLASK_APP=run.py`.

Специфичные паттерны и подводные камни
- Смешение подходов к БД: часть кода работает через Flask-SQLAlchemy-модели, а часть — через «сырые» SQL-запросы и свой `declarative Base`. При работе с legacy-данными следуйте примеру в `app/routes/people.py` и `app/models/practic.py`.
- Русские имена колонок: таблица `practic2` использует названия колонок на русском (например, `"ФИО"`, `"Номер_телефона"`). Запросы и вставки ссылаются на эти имена — не меняйте их без проверки.
- Конфликт маршрутов: `docs_bp` зарегистрирован с префиксом `/documents`, а `people_bp` также содержит маршруты на `/documents`. Следите за пересечениями URL при создании новых маршрутов.
- Доступ к БД через контекст Flask: в роутерах часто используется `current_app.extensions['sqlalchemy']` и `db.session.execute(db.text(...))` для raw SQL. Для коммита используйте шаблон try/except + rollback, как в `app/routes/people.py`.
- Авторизация и роли: используется `flask_login`. Защищайте маршруты декоратором `@login_required` и проверяйте `current_user.role == 'admin'` (пример в `app/routes/documents.py`).
- Несоответствие `requirements.txt`: в списке зависимостей указаны `fastapi`/`uvicorn` и другие пакеты, хотя код — Flask-приложение. Уточните, нужно ли синхронизировать `requirements.txt`.

Файлы для проверки при изменениях
- Точка входа: `run.py` (создаёт админа при первом запуске)
- Фабрика приложения: `app/__init__.py`
- Модели Flask-SQLAlchemy: `app/models/*.py`
- Legacy-модель: `app/models/practic.py` и `instance/database.py`
- Маршруты: `app/routes/*.py` (особенно `documents.py`, `people.py`, `auth.py`)
- Шаблоны: `templates/` (включая `document_form.html`, `clients.html`, `documents.html`)

Конкретные примеры (копировать и использовать)
- Raw SQL вставка (пример из `people.py`):
```
sql = db.text("""INSERT INTO practic2 ("ФИО", ...) VALUES (:fio, ...)""")
db.session.execute(sql, {"fio": value, ...})
db.session.commit()
```
- Обычное использование Flask-SQLAlchemy (пример из `documents.py`):
```
doc = Document(...)
db.session.add(doc)
db.session.commit()
```

При добавлении нового кода
- Регистрируйте новый blueprint в `app/__init__.py` (импортировать, затем `app.register_blueprint(...)`).
- Если меняете схему БД — используйте Flask-Migrate: установите `FLASK_APP=run.py` и выполните `flask db migrate` / `flask db upgrade`.

Вопросы владельцу репозитория
- Нужно ли привести `requirements.txt` в соответствие с Flask (удалить FastAPI/uvicorn), или есть отдельный сервис на FastAPI?
- Какой желаемый рабочий процесс миграций — вручную или через CI? Поделитесь примером команд, если он отличается.

Если что-то непонятно — укажите файлы или желаемые сценарии, я обновлю инструкции.
