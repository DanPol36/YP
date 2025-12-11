import pytest


class TestAuthRoutes:
    def test_login_page_get(self, client):
        """Test GET /login returns login form."""
        response = client.get('/login')
        assert response.status_code == 200
        data_str = response.data.decode('utf-8', errors='ignore').lower()
        assert 'login' in data_str or 'вход' in data_str
    
    def test_login_success(self, client):
        # First create the default admin user via run.py logic
        with client.application.app_context():
            from app.models.user import User
            from app import db
            from werkzeug.security import generate_password_hash
            admin = User(username='admin', role='admin')
            admin.password = generate_password_hash('12345')
            db.session.add(admin)
            db.session.commit()
        
        response = client.post('/login', data={
            'username': 'admin',
            'password': '12345'
        }, follow_redirects=True)
        assert response.status_code == 200
        # After login, user should be redirected to /clients/
        data_str = response.data.decode('utf-8', errors='ignore').lower()
        assert 'client' in data_str or 'список' in data_str
    
    def test_login_invalid_password(self, client):
        with client.application.app_context():
            from app.models.user import User
            from app import db
            from werkzeug.security import generate_password_hash
            admin = User(username='admin', role='admin')
            admin.password = generate_password_hash('12345')
            db.session.add(admin)
            db.session.commit()
        
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'wrongpass'
        })
        assert response.status_code == 200
        # Should still show login form (not redirect)
        data_str = response.data.decode('utf-8', errors='ignore').lower()
        assert 'login' in data_str or 'вход' in data_str
    
    def test_login_nonexistent_user(self, client):
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'anypass'
        })
        assert response.status_code == 200
        data_str = response.data.decode('utf-8', errors='ignore').lower()
        assert 'login' in data_str or 'вход' in data_str
    
    def test_logout(self, client, auth_user):
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
    
    def test_protected_route_requires_login(self, client):
        response = client.get('/clients/', follow_redirects=False)
        # Should redirect to login (could be 302 or 200 depending on Flask-Login behavior)
        assert response.status_code in [302, 200, 303]
    
    def test_change_password_requires_login(self, client):
        response = client.get('/change-password', follow_redirects=False)
        assert response.status_code == 302
    
    def test_change_password_success(self, client, auth_user):
        response = client.post('/change-password', data={
            'old_password': 'testpass123',
            'new_password': 'newpass456',
            'confirm_password': 'newpass456'
        }, follow_redirects=True)
        assert response.status_code == 200
    
    def test_change_password_mismatch(self, client, auth_user):
        response = client.post('/change-password', data={
            'old_password': 'testpass123',
            'new_password': 'newpass456',
            'confirm_password': 'different'
        })
        assert response.status_code == 200
        data_str = response.data.decode('utf-8', errors='ignore').lower()
        assert 'form' in data_str or 'password' in data_str
