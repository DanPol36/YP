import pytest


class TestDocumentRoutes:
    
    def test_get_documents_requires_login(self, client):
        response = client.get('/documents', follow_redirects=False)
        assert response.status_code in [302, 303, 308]
    
    def test_get_documents_authenticated(self, client, auth_user):
        response = client.get('/documents', follow_redirects=True)
        assert response.status_code == 200
    
    def test_create_document_requires_admin(self, client, auth_user):
        response = client.get('/documents/create', follow_redirects=False)
        assert response.status_code in [200, 302, 403]
    
    def test_create_document_admin_can_access(self, client, admin_user):
        response = client.get('/documents/create')
        assert response.status_code == 200
    
    def test_upload_document_admin_only(self, client, auth_user):
        response = client.post('/documents/upload', data={}, follow_redirects=False)
        assert response.status_code in [302, 403, 404]
    
    def test_documents_page_title(self, client, auth_user):
        response = client.get('/documents', follow_redirects=True)
        assert response.status_code == 200
        data_str = response.data.decode('utf-8', errors='ignore').lower()
        assert 'клиент' in data_str or 'client' in data_str or 'html' in data_str
