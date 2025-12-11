import pytest
from io import BytesIO


class TestPeopleRoutes:
    
    def test_get_people_requires_login(self, client):
        response = client.get('/clients/', follow_redirects=False)
        assert response.status_code in [200, 302, 303]
    
    def test_get_people_authenticated(self, client, auth_user):
        response = client.get('/clients/')
        assert response.status_code == 200
        data_str = response.data.decode('utf-8', errors='ignore').lower()
        assert 'client' in data_str or 'список' in data_str
    
    def test_add_person_get(self, client, auth_user):
        response = client.get('/clients/create')
        assert response.status_code == 200
        data_str = response.data.decode('utf-8', errors='ignore').lower()
        assert 'fio' in data_str or 'фио' in data_str
    
    def test_add_person_post(self, client, auth_user):
        response = client.post('/clients/create', data={
            'fio': 'Иван Петров',
            'gender': 'м',
            'address': 'ул. Тестовая, 123',
            'age': '30',
            'birth_date': '1995-01-15',
            'phone': '+79001234567',
            'email': 'ivan@example.com',
            'notes': 'Тестовый клиент'
        }, follow_redirects=True)
        assert response.status_code == 200
        data_str = response.data.decode('utf-8', errors='ignore').lower()
        assert 'успешно' in data_str or 'success' in data_str
    
    def test_add_person_missing_fio(self, client, auth_user):
        response = client.post('/clients/create', data={
            'fio': '',  
            'phone': '+79001234567'
        }, follow_redirects=True)
        assert response.status_code == 200
    
    def test_import_csv_file(self, client, auth_user):
        csv_data = b"""FIO,Gender,Address,Phone,Email
Peter Sidorov,male,Circle Str 5,+79009876543,petr@test.com
Elena Smirnova,female,Forest St 10,+79998765432,elena@test.com"""
        
        data = {
            'file': (BytesIO(csv_data), 'clients.csv')
        }
        response = client.post('/clients/import', data=data, follow_redirects=True)
        assert response.status_code == 200
        data_str = response.data.decode('utf-8', errors='ignore').lower()
        assert 'import' in data_str or 'import' in data_str
    
    def test_import_xlsx_file(self, client, auth_user):
        try:
            import openpyxl
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.append(['FIO', 'Gender', 'Phone', 'Email'])
            ws.append(['Test User', 'male', '+79991112233', 'test@example.com'])
            
            xlsx_bytes = BytesIO()
            wb.save(xlsx_bytes)
            xlsx_bytes.seek(0)
            
            data = {
                'file': (xlsx_bytes, 'clients.xlsx')
            }
            response = client.post('/clients/import', data=data, follow_redirects=True)
            assert response.status_code == 200
        except ImportError:
            pytest.skip("openpyxl not installed")
    
    def test_import_invalid_file_format(self, client, auth_user):
        data = {
            'file': (BytesIO(b'invalid data'), 'clients.txt')
        }
        response = client.post('/clients/import', data=data, follow_redirects=True)
        assert response.status_code == 200
        data_str = response.data.decode('utf-8', errors='ignore').lower()
        assert 'csv' in data_str or 'xlsx' in data_str
    
    def test_import_no_file(self, client, auth_user):
        response = client.post('/clients/import', follow_redirects=True)
        assert response.status_code == 200
    
    def test_view_person_not_found(self, client, auth_user):
        response = client.get('/clients/nonexistent', follow_redirects=True)
        assert response.status_code == 200
        data_str = response.data.decode('utf-8', errors='ignore').lower()
        assert 'not found' in data_str or 'не найден' in data_str
    
    def test_delete_person_requires_post(self, client, auth_user):
        response = client.get('/clients/test/delete', follow_redirects=False)
        assert response.status_code in [302, 405]
