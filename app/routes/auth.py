from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from ..models.user import User
from flask import current_app

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    db = current_app.extensions['sqlalchemy']
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('people.get_people'))
        flash('Неверные данные', 'danger')
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    db = current_app.extensions['sqlalchemy']
    logout_user()
    return redirect(url_for('auth.login'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    db = current_app.extensions['sqlalchemy']
    if request.method == 'POST':
        # Поддерживаем оба имени поля: old_password или current_password
        current_password = request.form.get('current_password') or request.form.get('old_password')
        new_password = request.form.get('new_password')
        new_password2 = request.form.get('new_password2')

        # Валидация полей
        if not current_password or not new_password or not new_password2:
            flash('Заполните все поля', 'danger')
        elif not check_password_hash(current_user.password, current_password):
            flash('Неверный текущий пароль', 'danger')
        elif new_password != new_password2:
            flash('Пароли не совпадают', 'danger')
        else:
            current_user.password = generate_password_hash(new_password)
            db.session.commit()
            flash('Пароль изменён', 'success')
            return redirect(url_for('people.get_people'))
    return render_template('change_password.html')