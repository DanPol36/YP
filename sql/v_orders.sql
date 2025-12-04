-- SQL view / query: orders with link to clients (best-effort)
-- Этот запрос пытается связать заказы из order2 с клиентами из practic2 по номерам телефонов (digits-only)
-- и/или по ФИО. При необходимости адаптируйте имена колонок под вашу схему.

SELECT
  COALESCE(NULLIF(o."id",''), NULL) AS order_id,
  -- original client columns in order table (if present)
  COALESCE(NULLIF(o."ФИО",''), '')::text AS order_fio,
  regexp_replace(COALESCE(NULLIF(o."Номер_телефона",''),''), '\\D', '', 'g') AS order_phone_digits,
  COALESCE(NULLIF(o."Статус",''),'')::text AS status,
  COALESCE(NULLIF(o."Сумма",''), '')::text AS amount_text,
  COALESCE(NULLIF(o."Дата_создания",''), '')::text AS order_date_text,

  -- linked client (best-effort join)
  pr."ФИО" AS client_fio,
  regexp_replace(COALESCE(NULLIF(pr."Номер_телефона",''),''), '\\D', '', 'g') AS client_phone_digits,
  pr."Почта" AS client_email,

  -- computed: how we matched
  CASE
    WHEN regexp_replace(COALESCE(NULLIF(o."Номер_телефона",''),''), '\\D', '', 'g') <> ''
         AND regexp_replace(COALESCE(NULLIF(o."Номер_телефона",''),''), '\\D', '', 'g') = regexp_replace(COALESCE(NULLIF(pr."Номер_телефона",''),''), '\\D', '', 'g')
      THEN 'phone'
    WHEN COALESCE(NULLIF(o."ФИО",''),'') <> '' AND COALESCE(NULLIF(o."ФИО",''),'') = COALESCE(NULLIF(pr."ФИО",''),'')
      THEN 'fio'
    ELSE 'unmatched'
  END AS matched_by

FROM order2 o
LEFT JOIN practic2 pr
  ON (
       (regexp_replace(COALESCE(NULLIF(o."Номер_телефона",''),''), '\\D', '', 'g') <> ''
        AND regexp_replace(COALESCE(NULLIF(o."Номер_телефона",''),''), '\\D', '', 'g') = regexp_replace(COALESCE(NULLIF(pr."Номер_телефона",''),''), '\\D', '', 'g'))
    OR (COALESCE(NULLIF(o."ФИО",''),'') <> '' AND COALESCE(NULLIF(o."ФИО",''),'') = COALESCE(NULLIF(pr."ФИО",''),''))
  )
;
