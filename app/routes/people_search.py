from typing import Any, Dict, List, Tuple
from flask import current_app
from sqlalchemy import text
import re


def _normalize_gender_input(raw: str) -> Dict[str, str]:
	if not raw:
		return {"pattern": None, "initial": None}
	v = raw.strip().lower()
	if not v:
		return {"pattern": None, "initial": None}
	if v.startswith("м") or v.startswith("m"):
		return {"pattern": "%муж%", "initial": "м"}
	if v.startswith("ж") or v.startswith("f"):
		return {"pattern": "%жен%", "initial": "ж"}
	return {"pattern": f"%{v}%", "initial": v[0]}


def _digits_only(s: str) -> str:
	return re.sub(r"\D", "", s or "")


def search_people(db: Any, args: Dict[str, Any]) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
	"""Search people by filters.

	Supported filters: fio, gender, phone, email, age
	Returns (people_list, filters_dict)
	"""
	filters: Dict[str, Any] = {}
	where_clauses: List[str] = []
	params: Dict[str, Any] = {}

	fio = (args.get('fio') or '').strip()
	if fio:
		filters['fio'] = fio
		where_clauses.append('"ФИО" ILIKE :fio')
		params['fio'] = f"%{fio}%"

	phone = (args.get('phone') or '').strip()
	if phone:
		filters['phone'] = phone
		digits = _digits_only(phone)
		# compare only digits for phone, using Postgres regexp_replace
		# Use a safe empty-string fallback for the legacy phone column (avoid referencing a non-existent variant)
		where_clauses.append("regexp_replace(COALESCE(\"Номер_телефона\", ''), '\\D', '', 'g') LIKE :phone_digits")
		params['phone_digits'] = f"%{digits}%"

	email = (args.get('email') or '').strip()
	if email:
		filters['email'] = email
		where_clauses.append('"Почта" ILIKE :email')
		params['email'] = f"%{email}%"

	age = (args.get('age') or '').strip()
	if age:
		filters['age'] = age
		try:
			params['age'] = int(age)
			where_clauses.append('"Возраст" = :age')
		except ValueError:
			where_clauses.append('CAST("Возраст" AS TEXT) ILIKE :age')
			params['age'] = f"%{age}%"

	gender_raw = (args.get('gender') or '').strip()
	gender_norm = _normalize_gender_input(gender_raw)
	if gender_norm.get('pattern'):
		filters['gender'] = gender_raw
		where_clauses.append('(lower("Пол") LIKE lower(:gender_pattern) OR left(lower("Пол"),1) = :gender_initial)')
		params['gender_pattern'] = gender_norm['pattern']
		params['gender_initial'] = gender_norm['initial']

	# If no filters, return full select (previous behavior)
	if not where_clauses:
		full_sql = '''
			SELECT
				"ФИО" AS fio,
				"Пол" AS gender,
				"Адрес" AS address,
				"Возраст" AS age,
				"Дата_рождения"::text AS birth_date,
				COALESCE("Номер_телефона", '') AS phone,
				"Почта" AS email,
				"Примечания" AS notes
			FROM practic2
			ORDER BY "ФИО"
		'''
		try:
			current_app.logger.debug('search_people: running full select (no filters)')
			result = db.session.execute(text(full_sql)).mappings().fetchall()
			people = [dict(r) for r in result]
			current_app.logger.info('search_people: full select returned %d rows', len(people))
			return people, filters
		except Exception:
			try:
				db.session.rollback()
			except Exception:
				pass
			current_app.logger.exception('search_people: database error on full select')
			return [], filters

	base_sql = '''
		SELECT
			"ФИО" AS fio,
			"Пол" AS gender,
			"Возраст" AS age,
			COALESCE("Номер_телефона", '') AS phone,
			"Почта" AS email
		FROM practic2
	'''
	base_sql += '\n WHERE ' + '\n AND '.join(where_clauses)
	base_sql += '\n ORDER BY "ФИО"'
	base_sql += '\n LIMIT 1000'

	try:
		current_app.logger.debug('search_people: SQL -> %s', base_sql)
		current_app.logger.debug('search_people: params -> %s', params)
		result = db.session.execute(text(base_sql), params).mappings().fetchall()
		people = [dict(r) for r in result]
		current_app.logger.info('search_people: filtered select returned %d rows', len(people))
		return people, filters
	except Exception:
		try:
			db.session.rollback()
		except Exception:
			pass
		current_app.logger.exception('search_people: database error')
		return [], filters