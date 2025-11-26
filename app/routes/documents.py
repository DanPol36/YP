from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from flask import current_app
from ..models.document import Document
from datetime import datetime

docs_bp = Blueprint('docs', __name__, url_prefix='/documents')

@docs_bp.route('/')
@login_required
def index():
    db = current_app.extensions['sqlalchemy']
    documents = Document.query.all()
    return render_template('documents.html', documents=documents)

@docs_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    db = current_app.extensions['sqlalchemy']
    if request.method == 'POST':
        birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d').date()
        doc = Document(
            full_name=request.form['full_name'],
            birth_date=birth_date,
            phone=request.form['phone'],
            email=request.form.get('email', ''),
            address=request.form.get('address', ''),
            notes=request.form.get('notes', ''),
            owner_id=current_user.id
        )
        db.session.add(doc)
        db.session.commit()
        flash('Клиент добавлен!', 'success')
        return redirect(url_for('docs.index'))
    return render_template('document_form.html')

@docs_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    db = current_app.extensions['sqlalchemy']
    doc = Document.query.get_or_404(id)
    if doc.owner_id != current_user.id and current_user.role != 'admin':
        flash('Нет доступа!', 'danger')
        return redirect(url_for('docs.index'))

    if request.method == 'POST':
        doc.full_name = request.form['full_name']
        doc.birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d').date()
        doc.phone = request.form['phone']
        doc.email = request.form.get('email', '')
        doc.address = request.form.get('address', '')
        doc.notes = request.form.get('notes', '')
        db.session.commit()
        flash('Клиент обновлён!', 'success')
        return redirect(url_for('docs.index'))
    return render_template('document_form.html', doc=doc)

@docs_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    db = current_app.extensions['sqlalchemy']
    doc = Document.query.get_or_404(id)
    if doc.owner_id != current_user.id and current_user.role != 'admin':
        flash('Нет доступа!', 'danger')
        return redirect(url_for('docs.index'))
    db.session.delete(doc)
    db.session.commit()
    flash('Клиент удалён', 'success')
    return redirect(url_for('docs.index'))