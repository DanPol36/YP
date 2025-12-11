import pytest
import os
from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='session')
def app():
    app = create_app()
    # Use in-memory SQLite for tests
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    return app


@pytest.fixture(scope='function')
def client(app):
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def auth_user(client):
    with client.application.app_context():
        user = User(username='testuser', role='user')
        user.password = generate_password_hash('testpass123')
        db.session.add(user)
        db.session.commit()
    
    # Log in the user
    client.post('/login', data={
        'username': 'testuser',
        'password': 'testpass123'
    })
    return user


@pytest.fixture
def admin_user(client):
    with client.application.app_context():
        user = User(username='admin', role='admin')
        user.password = generate_password_hash('adminpass123')
        db.session.add(user)
        db.session.commit()
    
    # Log in the admin
    client.post('/login', data={
        'username': 'admin',
        'password': 'adminpass123'
    })
    return user
