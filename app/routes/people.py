# app/routes/people.py
from flask import Blueprint, render_template, request, current_app, redirect, url_for, flash

# Используем префикс `/clients`, чтобы не конфликтовать с `/documents`
people_bp = Blueprint('people', __name__, url_prefix='/clients', template_folder='../templates')


@people_bp.route('/')
def get_people():
    db = current_app.extensions['sqlalchemy']
    query = db.text("""
        SELECT
            "ФИО" AS fio, "Пол" AS gender, "Адрес" AS address, "Возраст" AS age,
            "Дата_рождения" AS birth_date, "Номер_телефона" AS phone,
            "Почта" AS email, "Примечания" AS notes
        FROM practic2
        ORDER BY "ФИО"
    """)
    result = db.session.execute(query).mappings().fetchall()
    people = [dict(row) for row in result]
    return render_template("clients.html", people=people)


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


# ——— РЕДАКТИРОВАНИЕ КЛИЕНТА ———
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
    query = db.text('SELECT * FROM practic2 WHERE "ФИО" = :fio')
    person = db.session.execute(query, {"fio": fio}).mappings().one_or_none()
    if not person:
        flash('Клиент не найден', 'warning')
        return redirect(url_for('people.get_people'))

    return render_template("person_form.html", person=dict(person))


@people_bp.route('/<path:fio>', methods=['GET'])
def view_person(fio):
    db = current_app.extensions['sqlalchemy']
    query = db.text('SELECT * FROM practic2 WHERE "ФИО" = :fio')
    person = db.session.execute(query, {"fio": fio}).mappings().one_or_none()
    if not person:
        flash('Клиент не найден', 'warning')
        return redirect(url_for('people.get_people'))
    return render_template('person_view.html', person=dict(person))


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