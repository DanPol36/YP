**Architecture Diagram**

- **File:** `docs/architecture_diagram.mmd` — Mermaid source diagram in Russian.
- **Purpose:** показывает общую структуру приложения: точку входа `run.py`, Flask-приложение `app/` (фабрика, роуты, модели, шаблоны), legacy-слой с `instance/database.py` и `practic2`, модель `Order`/`order2`, а также папки `scripts/` и `migrations/`.
- **How to render:**
  - Install mermaid-cli (Node.js required): `npm i -g @mermaid-js/mermaid-cli`.
  - Render to SVG: `mmdc -i docs/architecture_diagram.mmd -o docs/architecture_diagram.svg`.

- **Notes & Key Points:**
  - Legacy таблицы (`practic2`, `order2`) используют русские имена колонок; приложение сочетает Flask-SQLAlchemy и raw SQL через `instance.database.Base`.
  - Поиск клиентов (`app/routes/people_search.py`) делает агрегированный LEFT JOIN на `order2` для подсчёта `orders_count` и использует COALESCE для вариантов колонки телефона.
  - Миграции (Alembic) и вспомогательные SQL-скрипты находятся в `migrations/` и `scripts/`.
