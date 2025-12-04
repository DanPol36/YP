# Metabase (локальный запуск через Docker)

Этот файл объясняет, как запустить Metabase локально с тестовой Postgres (через `docker-compose`) и как запустить Metabase, чтобы он использовал внешнюю (реальную) базу данных проекта.

1) Убедитесь, что установлен Docker / Docker Compose.

2) Из корня репозитория выполните (PowerShell):

```powershell
docker compose up -d
```

3) Подождите, пока контейнеры поднятся; затем откройте в браузере:

http://localhost:3000

4) Первоначальная настройка:
- Создайте администратора (email + пароль).
- Metabase сам использует тестовую Postgres (образ `postgres:15`) как базу метаданных — параметры заданы в `docker-compose.yml`.

5) Подключение вашей рабочей БД (заменить тестовую):
- В Metabase: Admin → Databases → Add database → PostgreSQL.
- Если вы хотите подключить реальную БД проекта, в поле `Host` укажите адрес/хост вашей БД. Если Metabase запущен в Docker на той же машине, где работает Postgres вне Docker — используйте `host.docker.internal` как `Host`.

6) Остановка и удаление (тестовый compose):

```powershell
docker compose down
```

Если нужно, могу добавить SQL-файлы с `CREATE VIEW` для `practic2`/`order2`, чтобы удобнее работать с таблицами в Metabase. Хотите, чтобы я добавил их в `sql/`?

---

## Использовать внешнюю (реальную) базу данных проекта

Если вы хотите, чтобы Metabase использовал вашу реальную Postgres (а не тестовую из `docker-compose.yml`), есть готовый `docker-compose.metabase.external.yml`. Он запускает только сервис Metabase и читает настройки подключения из файла окружения.

Шаги:

1. Скопируйте пример файла окружения и заполните реальными данными:

```powershell
copy .env.metabase.example .env.metabase
# затем отредактируйте .env.metabase и пропишите реальные значения
```

2. Запустите Metabase с использованием внешнего файла compose и файла окружения:

```powershell
docker compose -f docker-compose.metabase.external.yml --env-file .env.metabase up -d
```

3. Проверка логов и состояния:

```powershell
docker compose -f docker-compose.metabase.external.yml logs -f metabase
docker compose -f docker-compose.metabase.external.yml ps
```

4. После запуска Metabase будет использовать указанную БД для своих метаданных. Если вы хотите, чтобы Metabase также брал данные для отчетов из той же базы проекта, добавьте эту же базу как источник данных в Metabase (Admin → Databases) — укажите хост/порт/имя БД и учётку для чтения данных.

Подсказки:
- Если ваш Postgres работает на той же машине и вы используете Docker Desktop на Windows/Mac, укажите `host.docker.internal` как `MB_DB_HOST` в `.env.metabase`.
- Если подключение проваливается — проверьте firewall, правильность пароля, и что база доступна по сети из Docker.
# Metabase (локальный запуск через Docker)

Этот файл объясняет, как запустить Metabase локально с тестовой Postgres (через `docker-compose`).

1) Убедитесь, что установлен Docker / Docker Compose.

2) Из корня репозитория выполните (PowerShell):

```powershell
docker compose up -d
```

3) Подождите, пока контейнеры поднятся; затем откройте в браузере:

http://localhost:3000

4) Первоначальная настройка:
- Создайте администратора (email + пароль).
- Metabase сам использует тестовую Postgres (образ `postgres:15`) как базу метаданных — параметры заданы в `docker-compose.yml`.

5) Подключение вашей рабочей БД (заменить тестовую):
- В Metabase: Admin → Databases → Add database → PostgreSQL.
- Если вы хотите подключить реальную БД проекта, в поле `Host` укажите адрес/хост вашей БД. Если Metabase запущен в Docker на той же машине, где работает Postgres вне Docker — используйте `host.docker.internal` как `Host`.

6) Остановка и удаление:

```powershell
docker compose down
```

Если нужно, могу добавить SQL-файлы с `CREATE VIEW` для `practic2`/`order2`, чтобы удобнее работать с таблицами в Metabase. Хотите, чтобы я добавил их в `sql/`? 
