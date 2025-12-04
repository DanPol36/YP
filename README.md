# YP — простое Flask-приложение для документов и клиентов

Это лёгкое приложение на Flask для работы с документами и базой клиентов. В репозитории есть код приложения, шаблоны, модели и несколько вспомогательных скриптов для профилирования и обслуживания.

Ниже — краткое и понятное описание того, что внутри и как с этим работать. Я постарался писать просто и без примеров команд.

## Что в репозитории
- Приложение на Flask с фабрикой приложения и зарегистрированными blueprint'ами для авторизации, документов и клиентов.
- Модели и часть кода на Flask-SQLAlchemy; есть отдельная legacy-модель для таблицы practiс2 с русскими именами колонок.
- Jinja2-шаблоны для страниц в папке app/templates.
- Набор утилит и скриптов в папке scripts и несколько помощников в корне для профилирования.

## Быстрый старт (в простых словах)
- Подготовьте Python-окружение и установите зависимости из requirements.txt.
- Создайте файл с настройками окружения и укажите строку подключения к базе данных и секрет для приложения.
- Запустите приложение как обычный Python-скрипт — при первом запуске создаётся администратор по умолчанию.

Если нужно, я могу добавить пошаговые инструкции для Windows/WSL/Linux отдельно.

## Docker и Metabase — что и зачем
- В проекте есть варианты для работы через Docker и для быстрого запуска Metabase — это удобно, если вы хотите быстро увидеть аналитику по данным.
- Что даёт Docker здесь: позволяет поднять Postgres и Metabase в контейнерах, не настраивая всё вручную на системе. Это удобно для тестов и локального анализа.
- Что такое Metabase: простой визуальный инструмент для создания запросов, графиков и дешбордов поверх вашей базы данных. Его удобно использовать, чтобы быстро получить отчёты по клиентам и заказам.

Коротко о вариантах использования:
- Если вы хотите всё запустить в контейнерах, в проекте есть готовые конфигурации для поднятия сервиса базы данных и Metabase. После старта Metabase становится доступен в браузере и можно добавить в него вашу базу.
- Если приложение вы запускаете локально (не в Docker), Metabase можно запустить отдельно и подключить к вашей базе: Metabase умеет работать с внешними Postgres-серверами.

Несколько практических замечаний (без команд):
- Когда Metabase работает в контейнере, а Postgres — на хосте, для подключения внутри контейнера нужно использовать специальный адрес, который позволяет контейнеру достучаться до хоста.
- В репозитории есть пример настроек окружения для Metabase и краткие инструкции, как подключать базу — их можно посмотреть и адаптировать под вашу систему.
- Перед удалением контейнеров или данных сделайте бэкап базы, если данные важны.

## База данных и legacy-таблица
- Основные модели находятся в app/models. Для работы с legacy-данными есть отдельная модель, которая использует русские имена колонок (это особенность — к ним нужно относиться осторожно при изменениях).
- Миграции настроены через Flask-Migrate; используйте их для изменения схемы, но учитывайте особенности legacy-таблицы.

## Шаблоны и маршруты — куда смотреть
- Шаблоны находятся в app/templates.
- Основные страницы приложения: вход/выход, изменение пароля, список документов и список/карточки клиентов.

## Профилирование и утилиты
- В папке scripts есть инструменты для создания профилей и генерации flamegraph-отчётов; эти скрипты помогают исследовать производительность.
- Также есть простая утилита для просмотра DOT-файлов в браузере.

## Важные замечания
- Legacy-таблица использует русские имена колонок; будьте внимательны при изменениях.
- В конфигурационных файлах и окружении не храните секреты в публичных репозиториях.
- Для продакшена стоит привязать версии зависимостей и настроить безопасное хранение секретов.

## Что я могу сделать дальше
- Добавить краткую пошаговую инструкцию для Windows/WSL/Linux.
- Добавить инструкции по Docker Compose и запуску Metabase с примерами переменных окружения (безопасно и без секретов).
- Подготовить CREATE VIEW-скрипты для Metabase, чтобы сразу получить удобные таблицы для аналитики.

Если хотите — напишите, какие разделы расширить или какие инструкции добавить, и я подготовлю их в простом понятном виде.
# YP — Flask Documents & Clients App

Simple Flask application for managing documents (clients) and a legacy clients table (practic2).

This repository contains a small Flask app + several helper scripts for profiling and maintenance.

---

## Highlights
- Flask application using app factory pattern (`create_app()` in `app/__init__.py`).
- Flask-SQLAlchemy as the ORM with a legacy SQL mapping defined in `instance/database.py` and `app/models/practic.py`.
- Blueprints in `app/routes/`: `auth`, `documents`, `people` (mapped to `/clients`).
- Basic user handling with `flask-login` (`User` in `app/models/user.py`) and admin auto-creation when the app first runs.
- Profiling helpers and conversion tools: `make_profile.py`, `scripts/profile_pyspy.ps1`, `scripts/convert_prof.ps1`, and a simple DOT viewer `tools/dot_viewer.html`.

---

## Requirements
- Python 3.11+ (or recent Python 3.x)
- Packages in `requirements.txt`:
  - Flask
  - Flask-SQLAlchemy
  - Flask-Login
  - Flask-Migrate
  - SQLAlchemy
  - python-dotenv
  - Jinja2

Install dependencies:
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## Configuration
Create a `.env` file at the project root with at least the following variables:
```
DATABASE_URL=postgresql+psycopg://user:pass@localhost/dbname
SECRET_KEY=your-secret
```

On first run, the script `run.py` will create database tables and an admin user with credentials:
- Username: `admin`
- Password: `12345`

**Note**: For production deployments, do not use `debug=True`, and change the admin password or create users via a script/CLI.

---

## Running the app (Development)
Start the app with either:
```powershell
# Option 1 - simple run
python run.py

# Option 2 - use Flask (ensure FLASK_APP is set)
set FLASK_APP=run.py
flask run
```

The app registers these blueprints: `/login`, `/logout`, `/change-password` (`auth`), `/documents` (`docs_bp`), and `/clients` (`people_bp`).

---

## Database & Models
- Regular SQLAlchemy models live in `app/models/` (e.g., `user.py`, `document.py`).
- `practic2` is a legacy table (Russian column names) mapped via a declarative `Base` in `instance/database.py` and `app/models/practic.py`.
  - BE CAREFUL modifying this migration-free table: column names use Cyrillic names
    (e.g., `"ФИО"`, `"Номер_телефона"`) which are accessed via raw SQL in `people.py` to avoid mapping conflicts.

To manage migrations with Flask-Migrate:
```powershell
set FLASK_APP=run.py
flask db init  # only once
flask db migrate -m "Initial"
flask db upgrade
```

---

## Templates & Views
- Templates are located in `app/templates/`.
- Important templates:
  - `layout.html` — base layout
  - `login.html` — login form
  - `clients.html`, `person_form.html`, `person_view.html` — list/create/edit/view pages for legacy `practic2` clients
  - `document_form.html`, `documents.html` — document handling pages

---

## Profiling & Flamegraphs
There are multiple ways to profile and view flamegraphs from cProfile or py-spy:

1. cProfile → pstats → gprof2dot → dot (Graphviz)
```powershell
# Generate the profile using the included test client script
python make_profile.py   # writes profile.prof

# Convert to DOT
pip install gprof2dot
python -m gprof2dot -f pstats profile.prof -o out.dot

# Convert to SVG (requires Graphviz `dot` available in PATH)
dot -Tsvg out.dot -o profile.svg
start profile.svg
```
We included `scripts/convert_prof.ps1` which automates gprof2dot and tries to call `dot` if available.

2. Using `py-spy` (sampling profiler) — useful for production-like profiling
```powershell
pip install py-spy
# We added a helper script which starts the app (optional), generates a load and records:
.\scripts\profile_pyspy.ps1 -StartServer -Duration 20 -Requests 100
```
This produces `flame_YYYYMMDD_HHMMSS.svg`.

3. `pyinstrument` produces an interactive HTML view
```powershell
pip install pyinstrument
pyinstrument -o profile.html -- python run.py
start profile.html
```

4. View DOT in-browser (no Graphviz required)
 - Open `tools/dot_viewer.html` in your browser. If you run a local file server (recommended) the tool will fetch `out.dot` automatically:
```powershell
python -m http.server 8000
# Then open http://localhost:8000/tools/dot_viewer.html
```
 - Or load `out.dot` using the file input and click `Render`.

---

## Utilities
- `scripts/remove_unneeded.py` — delete `__pycache__` directories and optionally empty `app/static/`.
- `tools/dot_viewer.html` — browser DOT viewer using viz.js (CDN) to render DOT files offline/online.

---

## Notes & Caveats
- Legacy `practic2` uses Russian column names — `app/routes/people.py` uses raw SQL with those column names to avoid issues with SQLAlchemy naming. Be careful when renaming or editing.
- The `run.py` script creates a default admin on the first run; remove or change this in production.
- Please pin dependency versions for production to ensure deterministic installs and reproducibility.

---

## Where to look next (high-level)
- `app/__init__.py` — app factory & blueprint registration
- `app/routes/` — application blueprints: `auth`, `documents`, `people`
- `app/models/*` — SQLAlchemy models
- `app/templates/*` — Jinja2 templates
- `scripts/*` — helper scripts for profiling and cleanup
- `make_profile.py` — example cProfile test client

---

If you want, I can:
- Add version pins to `requirements.txt`; or
- Add a small `docker-compose` example with Postgres; or
- Add unit tests for the CRUD endpoints.

Thanks! If you want edits to the README (in Russian or with additional examples), say which sections to expand.

