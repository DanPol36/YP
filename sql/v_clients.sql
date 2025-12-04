-- SQL view / query: normalized clients
-- Этот файл содержит пример запроса, который собирает удобную для аналитики таблицу клиентов
-- Используйте как CREATE VIEW v_clients AS ... или вставьте в Metabase как Native query

SELECT
  COALESCE(NULLIF("ID",''), NULL) AS id,
  COALESCE(NULLIF("ФИО",''), '')::text AS fio,
  -- digits-only phone
  regexp_replace(COALESCE(NULLIF("Номер_телефона",''),''), '\\D', '', 'g') AS phone_digits,
  COALESCE(NULLIF("Почта",''), '')::text AS email,
  COALESCE(NULLIF("Пол",''), '')::text AS gender,
  -- keep raw dob as text to avoid parse errors; compute age only when value looks like YYYY-MM-DD
  COALESCE(NULLIF("Дата_рождения",''), '')::text AS dob_text,
  CASE
    WHEN COALESCE(NULLIF("Дата_рождения",''),'') ~ '^\\d{4}-\\d{2}-\\d{2}$' THEN
      date_part('year', age(current_date, "Дата_рождения"::date))::int
    ELSE NULL
  END AS age_years,
  -- other useful fields (adjust names if your schema different)
  COALESCE(NULLIF("Номер_договора",''),'')::text AS contract_number,
  COALESCE(NULLIF("Адрес",''),'')::text AS address
FROM practic2 pr
;
