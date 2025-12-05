# app/routes/people.py
from flask import Blueprint, render_template, request, current_app, redirect, url_for, flash
import csv
import io
from werkzeug.utils import secure_filename
from .people_search import search_people

# Используем префикс `/clients`, чтобы не конфликтовать с `/documents`
people_bp = Blueprint('people', __name__, url_prefix='/clients', template_folder='../templates')


@people_bp.route('/import', methods=['POST'])
def import_clients():
    """Import clients from uploaded CSV or XLSX file.

    Supported formats: CSV (utf-8 or utf-8-sig) and XLSX (requires openpyxl).
    Expected columns (either Russian or English keys):
      ФИО / fio
      Пол / gender
      Адрес / address
      Возраст / age
      Дата_рождения / birth_date
      Номер_телефона / phone
      Почта / email
      Примечания / notes
    """
    db = current_app.extensions['sqlalchemy']
    uploaded = request.files.get('file')
    if not uploaded:
        flash('Файл не загружен', 'warning')
        return redirect(url_for('people.get_people'))

    filename = secure_filename(uploaded.filename or '')
    if filename.lower().endswith('.csv'):
        stream = io.TextIOWrapper(uploaded.stream, encoding='utf-8-sig')
        reader = csv.DictReader(stream)
        rows = list(reader)
    elif filename.lower().endswith('.xlsx'):
        try:
            import openpyxl
        except Exception:
            flash('Для импорта XLSX требуется пакет openpyxl. Установите его и перезапустите.', 'danger')
            return redirect(url_for('people.get_people'))
        wb = openpyxl.load_workbook(uploaded, read_only=True)
        ws = wb.active
        it = ws.values
        try:
            headers = [str(h).strip() for h in next(it)]
        except StopIteration:
            flash('Файл пустой', 'warning')
            return redirect(url_for('people.get_people'))
        rows = []
        for r in it:
            row = {headers[i]: (r[i] if i < len(r) else '') for i in range(len(headers))}
            rows.append(row)
    else:
        flash('Поддерживаются только файлы .csv и .xlsx', 'warning')
        return redirect(url_for('people.get_people'))

    # map possible headers to target columns
    def map_row(r):
        # lowercase keys without spaces/underscores for flexible matching
        normalized = {}
        for k, v in r.items():
            if k is None:
                continue
            key = str(k).strip().lower().replace(' ', '_')
            normalized[key] = v

        def pick(*cands):
            for c in cands:
                kc = c.lower()
                if kc in normalized:
                    return normalized[kc]
            return None

        return {
            'fio': pick('ФИО', 'fio'),
            'gender': pick('Пол', 'gender'),
            'address': pick('Адрес', 'address'),
            'age': pick('Возраст', 'age'),
            'birth_date': pick('Дата_рождения', 'birth_date', 'birthdate'),
            'phone': pick('Номер_телефона', 'phone', 'phone_number', 'tel'),
            'email': pick('Почта', 'email', 'e-mail'),
            'notes': pick('Примечания', 'notes', 'comments')
        }

    success = 0
    failed = 0
    errors = []
    max_rows = current_app.config.get('IMPORT_MAX_ROWS', 2000)
    if len(rows) > max_rows:
        flash(f'Файл слишком большой ({len(rows)} строк). Ограничение {max_rows}.', 'danger')
        return redirect(url_for('people.get_people'))

    insert_sql = db.text('''
        INSERT INTO practic2 (
            "ФИО", "Пол", "Адрес", "Возраст",
            "Дата_рождения", "Номер_телефона", "Почта", "Примечания"
        ) VALUES (
            :fio, :gender, :address, :age,
            :birth_date, :phone, :email, :notes
        )
    ''')

    for idx, raw in enumerate(rows, start=1):
        mapped = map_row(raw)
        params = {
            'fio': mapped.get('fio') or '',
            'gender': mapped.get('gender') or None,
            'address': mapped.get('address') or None,
            'age': mapped.get('age') or None,
            'birth_date': mapped.get('birth_date') or None,
            'phone': mapped.get('phone') or None,
            'email': mapped.get('email') or None,
            'notes': mapped.get('notes') or None
        }
        try:
            db.session.execute(insert_sql, params)
            db.session.commit()
            success += 1
        except Exception as e:
            try:
                db.session.rollback()
            except Exception:
                pass
            failed += 1
            errors.append(f'Line {idx}: {e}')

    msg = f'Импорт завершён: {success} добавлено.'
    if failed:
        msg += f' {failed} ошибок.'
        current_app.logger.warning('Import clients: %s', errors[:5])
        flash(msg + ' Первые ошибки: ' + '; '.join(errors[:3]), 'warning')
    else:
        flash(msg, 'success')

    return redirect(url_for('people.get_people'))


@people_bp.route('/')
def get_people():
    db = current_app.extensions['sqlalchemy']
    people, filters = search_people(db, request.args)
    return render_template("clients.html", people=people, filters=filters)


# ——— ДОБАВЛЕНИЕ КЛИЕНТА ———
@people_bp.route('/create', methods=['GET', 'POST'])
def add_person():
    if request.method == 'POST':
        db = current_app.extensions['sqlalchemy']
        sql = db.text("""
            INSERT INTO practic2 (
                "ФИО", "Пол", "Адрес", "Возраст",
                "Дата_рождения", "Номер_телефона", "Почта", "Примечания"
            ) VALUES (
                :fio, :gender, :address, :age,
                :birth_date, :phone, :email, :notes
            )
        """)
        try:
            db.session.execute(sql, {
                "fio": request.form['fio'],
                "gender": request.form.get('gender'),
                "address": request.form.get('address'),
                "age": request.form.get('age') or None,
                "birth_date": request.form.get('birth_date') or None,
                "phone": request.form.get('phone'),
                "email": request.form.get('email'),
                "notes": request.form.get('notes')
            })
            db.session.commit()
            flash('Клиент успешно добавлен!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {e}', 'danger')
        return redirect(url_for('people.get_people'))

    return render_template("person_form.html", person=None)


#РЕДАКТИРОВАНИЕ КЛИЕНТА 
@people_bp.route('/<path:fio>/edit', methods=['GET', 'POST'])
def edit_person(fio):
    db = current_app.extensions['sqlalchemy']

    if request.method == 'POST':
        sql = db.text("""
            UPDATE practic2 SET
                "Пол" = :gender,
                "Адрес" = :address,
                "Возраст" = :age,
                "Дата_рождения" = :birth_date,
                "Номер_телефона" = :phone,
                "Почта" = :email,
                "Примечания" = :notes
            WHERE "ФИО" = :fio
        """)
        try:
            db.session.execute(sql, {
                "fio": fio,
                "gender": request.form.get('gender'),
                "address": request.form.get('address'),
                "age": request.form.get('age') or None,
                "birth_date": request.form.get('birth_date') or None,
                "phone": request.form.get('phone'),
                "email": request.form.get('email'),
                "notes": request.form.get('notes')
            })
            db.session.commit()
            flash('Клиент обновлён!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка: {e}', 'danger')
        return redirect(url_for('people.get_people'))

    # GET — показываем форму
    query = db.text('''
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
        WHERE "ФИО" = :fio
    ''')
    try:
        person = db.session.execute(query, {"fio": fio}).mappings().one_or_none()
    except Exception as e:
        current_app.logger.exception('view_orders: primary person select failed')
        # Fallback: try a simple SELECT * in case schema differs
        try:
            fallback = db.text('SELECT * FROM practic2 WHERE "ФИО" = :fio')
            prow = db.session.execute(fallback, {"fio": fio}).mappings().one_or_none()
            person = dict(prow) if prow else None
        except Exception:
            try:
                db.session.rollback()
            except Exception:
                pass
            person = None

    if not person:
        flash('Клиент не найден', 'warning')
        return redirect(url_for('people.get_people'))

    # Load related orders from order2 table. The legacy schema may use a long Russian column
    # name for the client key; detect a candidate column name dynamically.
    orders = []
    try:
        # find a column name in order2 that likely stores client key (contains 'клиент' or 'client')
        col_q = db.text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'order2' AND (column_name ILIKE '%клиент%' OR column_name ILIKE '%client%')
            LIMIT 1
        """)
        col_res = db.session.execute(col_q).fetchone()
        client_col = col_res[0] if col_res else None
        if client_col:
            # build safe SQL referencing the discovered column
            orders_sql = f"""
                SELECT * FROM order2
                WHERE COALESCE(\"{client_col}\", '') = :phone_exact
                   OR regexp_replace(COALESCE(\"{client_col}\", ''), '\\D', '', 'g') LIKE :phone_digits
                   OR COALESCE(\"{client_col}\", '') = :fio_exact
                   OR COALESCE(\"{client_col}\", '') = :id_text
                ORDER BY 1
            """
            params = {
                'phone_exact': person['Номер_телефона'] if person.get('Номер_телефона') else person.get('phone'),
                'phone_digits': '%' + (person.get('Номер_телефона') or person.get('phone') or '').replace('+', '').replace(' ', '').replace('(', '').replace(')', '').replace('-', '') + '%',
                'fio_exact': person.get('ФИО') or person.get('fio'),
                    'id_text': ''
            }
            ord_res = db.session.execute(db.text(orders_sql), params).mappings().fetchall()
            orders = [dict(r) for r in ord_res]
            # map displayed order number to per-client ordinal (1..N)
            if orders:
                # keep original primary key value, add a per-client ordinal for display
                id_key = None
                for k in orders[0].keys():
                    if 'номер' in k.lower() and 'заказ' in k.lower():
                        id_key = k
                        break
                if not id_key:
                    id_key = list(orders[0].keys())[0]
                for idx, o in enumerate(orders, start=1):
                    o['_ordinal'] = idx
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            pass

    return render_template("person_form.html", person=dict(person), orders=orders)


@people_bp.route('/<path:fio>', methods=['GET'])
def view_person(fio):
    db = current_app.extensions['sqlalchemy']
    query = db.text('''
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
        WHERE "ФИО" = :fio
    ''')
    person = db.session.execute(query, {"fio": fio}).mappings().one_or_none()
    if not person:
        flash('Клиент не найден', 'warning')
        return redirect(url_for('people.get_people'))
    return render_template('person_view.html', person=dict(person))


@people_bp.route('/<path:fio>/orders', methods=['GET'])
def view_orders(fio):
    db = current_app.extensions['sqlalchemy']
    # Load the person first
    query = db.text('''
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
        WHERE "ФИО" = :fio
    ''')
    person = db.session.execute(query, {"fio": fio}).mappings().one_or_none()
    if not person:
        flash('Клиент не найден', 'warning')
        return redirect(url_for('people.get_people'))

    orders = []
    try:
        # detect possible client key column in order2
        col_q = db.text("""
            SELECT column_name FROM information_schema.columns
            WHERE table_name = 'order2' AND (column_name ILIKE '%клиент%' OR column_name ILIKE '%client%')
            ORDER BY ordinal_position LIMIT 1
        """)
        col_res = db.session.execute(col_q).fetchone()
        client_col = col_res[0] if col_res else None
        if client_col:
            # prepare params for matching
            phone_val = person['Номер_телефона'] if person.get('Номер_телефона') else person.get('phone')
            digits = ''.join(ch for ch in (phone_val or '') if ch.isdigit())
            orders_sql = f"""
                SELECT * FROM order2
                WHERE COALESCE(\"{client_col}\", '') = :phone_exact
                   OR regexp_replace(COALESCE(\"{client_col}\", ''), '\\D', '', 'g') LIKE :phone_digits
                   OR COALESCE(\"{client_col}\", '') = :fio_exact
                   OR COALESCE(\"{client_col}\", '') = :id_text
                ORDER BY 1
            """
            params = {
                'phone_exact': phone_val,
                'phone_digits': f'%{digits}%',
                'fio_exact': person.get('ФИО') or person.get('fio'),
                'id_text': ''
            }
            ord_res = db.session.execute(db.text(orders_sql), params).mappings().fetchall()
            orders = [dict(r) for r in ord_res]
            # map displayed order number to per-client ordinal (1..N)
            if orders:
                # keep original primary key value, add a per-client ordinal for display
                id_key = None
                for k in orders[0].keys():
                    if 'номер' in k.lower() and 'заказ' in k.lower():
                        id_key = k
                        break
                if not id_key:
                    id_key = list(orders[0].keys())[0]
                for idx, o in enumerate(orders, start=1):
                    o['_ordinal'] = idx
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            pass

    return render_template('person_orders.html', person=dict(person), orders=orders)


@people_bp.route('/<path:fio>/orders/create', methods=['GET', 'POST'])
def create_order(fio):
    db = current_app.extensions['sqlalchemy']
    # load person
    query = db.text('''
        SELECT
            "ФИО" AS fio,
            COALESCE("Номер_телефона", '') AS phone
        FROM practic2
        WHERE "ФИО" = :fio
    ''')
    person = db.session.execute(query, {"fio": fio}).mappings().one_or_none()
    if not person:
        flash('Клиент не найден', 'warning')
        return redirect(url_for('people.get_people'))

    # detect order2 columns and metadata
    cols_meta = db.session.execute(db.text("""
        SELECT column_name, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'order2'
        ORDER BY ordinal_position
    """)).fetchall()
    cols = [r[0] for r in cols_meta]

    # choose client column (contains 'клиент' or 'client') or fallback to first column
    client_col = None
    for c in cols:
        if 'клиент' in c.lower() or 'client' in c.lower():
            client_col = c
            break
    if not client_col and cols:
        client_col = cols[0]

    # prefer phone as client identifier
    client_val = person.get('Номер_телефона') or person.get('phone') or person.get('ФИО') or person.get('fio') or fio

    # check for NOT NULL id-like column (e.g. номер_заказа) which needs a value
    id_column = None
    for col, is_nullable, col_default in cols_meta:
        if (is_nullable == 'NO') and (col_default is None):
            if 'номер' in col.lower() and 'заказ' in col.lower():
                id_column = col
                break
            if id_column is None:
                id_column = col

    # compute next id per-client if possible (MAX(id) WHERE client_col = client_val) else None
    next_id = None
    if id_column:
        try:
            # use a global next id (MAX + 1) to satisfy unique primary key constraints
            seq_q = db.text(f"SELECT COALESCE(MAX(CAST(\"{id_column}\" AS bigint)), 0) + 1 AS next_id FROM order2")
            seq_res = db.session.execute(seq_q).fetchone()
            next_id = seq_res[0]
        except Exception:
            try:
                db.session.rollback()
            except Exception:
                pass
            next_id = None
    # choose client column (contains 'клиент' or 'client') or fallback to first column
    client_col = None
    for c in cols:
        if 'клиент' in c.lower() or 'client' in c.lower():
            client_col = c
            break
    if not client_col and cols:
        client_col = cols[0]

    if request.method == 'POST':
        # prepare insert columns and params based on available columns
        insert_cols = []
        params = {}
        if client_col:
            insert_cols.append(f'"{client_col}"')
            # prefer phone, fallback to fio
            params['client_val'] = person.get('Номер_телефона') or person.get('phone') or person.get('fio') or fio

        # include computed id if needed
        if id_column and next_id is not None and id_column not in [c.replace('"', '') for c in insert_cols]:
            insert_cols.insert(0, f'"{id_column}"')
            params[id_column] = next_id

        # common candidate columns to fill from the form if present
        candidates = ['название', 'цена', 'примечания', 'статус_заказа']
        for cand in candidates:
            if cand in cols:
                insert_cols.append(f'"{cand}"')
                params[cand] = request.form.get(cand) or request.form.get(cand.replace('_', ' ')) or request.form.get(cand.replace(' ', '_')) or ''

        if not insert_cols:
            flash('Не удалось определить столбцы для вставки в order2', 'danger')
            return redirect(url_for('people.view_orders', fio=fio))

        cols_sql = ', '.join(insert_cols)
        # build parameter names aligned with insert_cols
        param_names = []
        for col in insert_cols:
            col_name = col.replace('"', '')
            if col_name == client_col:
                param_names.append('client_val')
            else:
                param_names.append(col_name)

        vals_sql = ', '.join(':' + name for name in param_names)
        insert_sql = f'INSERT INTO order2 ({cols_sql}) VALUES ({vals_sql})'

        # Ensure required NOT NULL columns without defaults are provided.
        try:
            col_meta_q = db.text("""
                SELECT column_name, is_nullable, column_default, data_type
                FROM information_schema.columns
                WHERE table_name = 'order2'
            """
            )
            meta = {r[0]: {'is_nullable': r[1], 'column_default': r[2], 'data_type': r[3]} for r in db.session.execute(col_meta_q).fetchall()}
        except Exception:
            meta = {}

        # For any param_name not present in params, and column is NOT NULL and has no default, try to generate a sensible value.
        for pname in param_names:
            if pname in params:
                continue
            colinfo = meta.get(pname)
            if not colinfo:
                # unknown column meta: default to empty string
                params[pname] = ''
                continue

            if colinfo['is_nullable'] == 'NO' and not colinfo['column_default']:
                cname = pname
                dtype = (colinfo.get('data_type') or '').lower()
                # if column name suggests a number/id, generate next integer
                if 'номер' in cname.lower() or 'id' in cname.lower() or 'num' in cname.lower() or dtype in ('integer', 'bigint'):
                    try:
                        max_q = db.text(f"SELECT COALESCE(MAX( (regexp_replace(COALESCE(\"{cname}\", ''),'\\D','', 'g'))::bigint ), 0) + 1 AS nextval FROM order2")
                        nv = db.session.execute(max_q).scalar()
                        params[pname] = int(nv or 1)
                    except Exception:
                        params[pname] = 1
                else:
                    # text-like required column: default to empty string
                    params[pname] = ''
            else:
                # nullable or has default: leave absent so DB default applies
                pass

        try:
            db.session.execute(db.text(insert_sql), params)
            db.session.commit()
            flash('Заказ добавлен', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception('create_order failed')
            flash(f'Ошибка при добавлении заказа: {e}', 'danger')
        return redirect(url_for('people.view_orders', fio=fio))

    # GET: render form
    return render_template('order_form.html', person=dict(person), order=None)


def _detect_order_pk_column(db):
    """Return primary key column name for table order2 or None."""
    try:
        pk_q = db.text("""
            SELECT kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
             AND tc.table_name = kcu.table_name
            WHERE tc.table_name = 'order2' AND tc.constraint_type = 'PRIMARY KEY'
            ORDER BY kcu.ordinal_position LIMIT 1
        """)
        r = db.session.execute(pk_q).fetchone()
        return r[0] if r else None
    except Exception:
        try:
            db.session.rollback()
        except Exception:
            pass
        return None


@people_bp.route('/<path:fio>/orders/<path:pk>/edit', methods=['GET', 'POST'])
def edit_order(fio, pk):
    db = current_app.extensions['sqlalchemy']
    # load person
    p_q = db.text('''
        SELECT
            "ФИО" AS fio,
            COALESCE("Номер_телефона", '') AS phone
        FROM practic2
        WHERE "ФИО" = :fio
    ''')
    person = db.session.execute(p_q, {"fio": fio}).mappings().one_or_none()
    if not person:
        flash('Клиент не найден', 'warning')
        return redirect(url_for('people.get_people'))

    pk_col = _detect_order_pk_column(db) or 'номер_заказа'

    if request.method == 'POST':
        # update allowed columns from form
        candidates = ['название', 'цена', 'примечания', 'статус_заказа']
        set_clauses = []
        params = {}
        for cand in candidates:
            if cand in candidates:
                val = request.form.get(cand)
                if val is not None:
                    set_clauses.append(f'"{cand}" = :{cand}')
                    params[cand] = val
        if not set_clauses:
            flash('Нет полей для обновления', 'warning')
            return redirect(url_for('people.view_orders', fio=fio))
        params['pk'] = pk
        sql = db.text(f'UPDATE order2 SET {", ".join(set_clauses)} WHERE "{pk_col}" = :pk')
        try:
            db.session.execute(sql, params)
            db.session.commit()
            flash('Заказ обновлён', 'success')
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception('edit_order failed')
            flash(f'Ошибка при обновлении заказа: {e}', 'danger')
        return redirect(url_for('people.view_orders', fio=fio))

    # GET: load order by pk
    sel = db.text(f'SELECT * FROM order2 WHERE "{pk_col}" = :pk')
    order = db.session.execute(sel, {"pk": pk}).mappings().one_or_none()
    if not order:
        flash('Заказ не найден', 'warning')
        return redirect(url_for('people.view_orders', fio=fio))
    return render_template('order_form.html', person=dict(person), order=dict(order))


@people_bp.route('/<path:fio>/orders/<path:pk>/delete', methods=['POST'])
def delete_order(fio, pk):
    db = current_app.extensions['sqlalchemy']
    pk_col = _detect_order_pk_column(db) or 'номер_заказа'
    try:
        sql = db.text(f'DELETE FROM order2 WHERE "{pk_col}" = :pk')
        db.session.execute(sql, {"pk": pk})
        db.session.commit()
        flash('Заказ удалён', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.exception('delete_order failed')
        flash(f'Ошибка при удалении заказа: {e}', 'danger')
    return redirect(url_for('people.view_orders', fio=fio))


@people_bp.route('/<path:fio>/delete', methods=['POST'])
def delete_person(fio):
    db = current_app.extensions['sqlalchemy']
    sql = db.text('DELETE FROM practic2 WHERE "ФИО" = :fio')
    try:
        db.session.execute(sql, {"fio": fio})
        db.session.commit()
        flash('Клиент удалён', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при удалении: {e}', 'danger')
    return redirect(url_for('people.get_people'))