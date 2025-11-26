from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()
    
    # Создаём админа при первом запуске
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password=generate_password_hash('12345'), role='admin')
        db.session.add(admin)
        db.session.commit()
        print("Админ создан → логин: admin | пароль: 12345")

if __name__ == '__main__':
    app.run(debug=True)