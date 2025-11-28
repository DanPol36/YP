# YP — Flask приложение для документов и клиентов

Небольшое Flask-приложение для управления документами и базой клиентов (legacy-таблица `practic`).

В репозитории есть приложение Flask, миграции, пользовательская авторизация и несколько утилит для профилирования/конвертации результатов профилирования.

---

## ✨ Ключевые моменты
- Приложение использует `create_app()` (фабрика) — см. `app/__init__.py`.
- ORM: `Flask-SQLAlchemy` + legacy-модель `practic2` (Cyrillic). Основная схема в `app/models/*.py`.
- Blueprints: `auth` (авторизация), `documents` (работа с документами), `people` (legacy клиенты, роуты доступны по `/clients`).
- Авторизация через `flask-login`, подключение миграций через `Flask-Migrate`.
- Скрипты для профилирования и преобразования пильных файлов сформированы в `scripts/` и корне: `make_profile.py`, `scripts/profile_pyspy.ps1`, `scripts/convert_prof.ps1`, `tools/dot_viewer.html`.

---

## 🛠️ Требования
- Python 3.11+ (или 3.x).
- Установленные зависимости: см. `requirements.txt`.

Установка зависимостей:
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 🔧 Конфигурация
Создайте файл `.env` в корне проекта и заполните переменные:
```
DATABASE_URL=postgresql+psycopg://user:pass@localhost/dbname
SECRET_KEY=ваш_секрет
```

При первом запуске `run.py` создаёт таблицы и автоматически создаёт администратора:
- Логин: `admin`
- Пароль: `12345`

⚠️ Для production: не используйте `debug=True`, измените пароль администратора и храните секрет в безопасном месте.

---

## ▶️ Запуск приложения (локально)
```powershell
# Быстрый вариант
python run.py

# Или с Flask CLI
set FLASK_APP=run.py
flask run
```

Приложение зарегистрирует маршруты:
- `/login`, `/logout`, `/change-password` (auth)
- `/documents` (docs_bp)
- `/clients` (people_bp)

---

## 💾 База данных и миграции
- Flask-SQLAlchemy и Flask-Migrate настроены в `app/__init__.py`.
- Legacy таблица `practic2` расположена в `app/models/practic.py` и использует русские имена колонок (например, `"ФИО"`, `"Номер_телефона"`). Для неё используются сырые SQL-запросы в `app/routes/people.py`.

Миграции:
```powershell
set FLASK_APP=run.py
flask db init      # выполнить один раз
flask db migrate -m "Initial"
flask db upgrade
```

---

## 🧭 Шаблоны и страницы
- Шаблоны: `app/templates/`.
- Важные шаблоны:
  - `layout.html` — базовый шаблон
  - `login.html` — форма входа
  - `clients.html`, `person_form.html`, `person_view.html` — список клиентов, форма (create/edit), просмотр
  - `document_form.html`, `documents.html` — документы

---

## 📈 Профилирование и флеймграфы
В проекте уже есть несколько утилит и скриптов для профилирования.

### 1) cProfile -> pstats -> gprof2dot -> dot (Graphviz)
```powershell
# Создаём пример профиля
python make_profile.py  # создаёт profile.prof

# Конвертация pstats -> dot
pip install gprof2dot
python -m gprof2dot -f pstats profile.prof -o out.dot

# Конвертация dot -> svg (требует Graphviz dot)
dot -Tsvg out.dot -o profile.svg
start profile.svg
```
Скрипт `scripts/convert_prof.ps1` пытается автоматизировать этот процесс и найти `dot`.

**Установка Graphviz (Windows)**:
```powershell
# winget
winget install --id Graphviz.Graphviz -e

# или Chocolatey
choco install graphviz -y
```

### 2) py-spy (sampling profiler) — рекомендуем для production-like профилирования
```powershell
pip install py-spy
# Запуск через helper-скрипт (создаёт flamegraph SVG)
.\scripts\profile_pyspy.ps1 -StartServer -Duration 20 -Requests 100
```

### 3) pyinstrument — быстрый HTML-отчёт
```powershell
pip install pyinstrument
pyinstrument -o profile.html -- python run.py
start profile.html
```

### 4) Просмотр DOT в браузере
Есть `tools/dot_viewer.html`, который использует viz.js для отрисовки DOT прямо в браузере.
Лучше запускать файл через HTTP-сервер, чтобы избежать блокировки браузером:
```powershell
python -m http.server 8000
# Откройте http://localhost:8000/tools/dot_viewer.html
```

---

## 🧰 Утилиты
- `scripts/remove_unneeded.py` — удаляет `__pycache__` и пустую папку `app/static`.
- `scripts/profile_pyspy.ps1` — помогает с py-spy (запуск, нагрузка и запись). См. комментарии в скрипте.
- `scripts/convert_prof.ps1` — конвертация `.prof` -> `.dot` -> `.svg` (при установленном Graphviz).
- `tools/dot_viewer.html` — офлайн/онлайн просмотр DOT.

---

## ⚠️ Важные замечания
- Legacy-таблица `practic2` использует русские имена колонок — осторожно при миграциях/переименованиях.
- Для production: не храните `SECRET_KEY` в `.env` в публичном репозитории, используйте секретный менеджер/CI.
- В тестовой нагрузке может проявляться высокое время хеширования паролей (scrypt) — нормально для безопасности, но учтите это при нагрузочном тесте.

---

## 📍 Куда смотреть дальше
- `app/__init__.py` — фабрика приложения и регистрация blueprint'ов
- `app/routes/` — реализованные маршруты
- `app/models/` — модели SQLAlchemy
- `app/templates/` — Jinja2 шаблоны
- `make_profile.py`, `scripts/*` — профилирование и утилиты

---

Если хотите — могу:
- закрепить версии в `requirements.txt` (рекомендуется для CI/production);
- добавить `docker-compose.yml` с PostgreSQL и окружением для быстрой локальной проверки;
- добавлять тесты и настройку CI (GitHub Actions).

Если нужно — переведу README на русский более подробно или добавлю пошаговые инструкции для Windows/WSL/Linux.
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

