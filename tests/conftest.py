"""
Shared fixtures for CRM Doctor E2E tests.
Uses real Supabase database — no mocking.
"""
import os
import uuid
import pytest
from dotenv import load_dotenv

load_dotenv()

from backend import create_app
from backend.extensions import get_supabase, _supabase_client


@pytest.fixture(scope='session')
def app():
    """Create Flask app for the entire test session."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    yield app


@pytest.fixture(scope='function')
def client(app):
    """Unauthenticated Flask test client."""
    return app.test_client()


@pytest.fixture(scope='session')
def supabase_client(app):
    """Direct Supabase client for DB-level tests."""
    with app.app_context():
        return get_supabase()


@pytest.fixture(scope='session')
def doctor_user(supabase_client):
    """Fetch the seeded doctor user."""
    result = supabase_client.table('users').select('*').eq('email', 'doctor@demo.com').execute()
    assert result.data, 'Doctor user not found — run seed first: python -m backend.seed.seed_data'
    return result.data[0]


@pytest.fixture(scope='session')
def secretary_user(supabase_client):
    """Fetch the seeded secretary user."""
    result = supabase_client.table('users').select('*').eq('email', 'secretary@demo.com').execute()
    assert result.data, 'Secretary user not found — run seed first'
    return result.data[0]


@pytest.fixture(scope='function')
def doctor_client(app, doctor_user):
    """Flask test client authenticated as doctor."""
    c = app.test_client()
    with c.session_transaction() as sess:
        sess['user_id'] = doctor_user['id']
        sess['user_email'] = doctor_user['email']
        sess['user_name'] = doctor_user['full_name']
        sess['user_role'] = 'doctor'
    return c


@pytest.fixture(scope='function')
def secretary_client(app, secretary_user):
    """Flask test client authenticated as secretary."""
    c = app.test_client()
    with c.session_transaction() as sess:
        sess['user_id'] = secretary_user['id']
        sess['user_email'] = secretary_user['email']
        sess['user_name'] = secretary_user['full_name']
        sess['user_role'] = 'secretary'
    return c


@pytest.fixture(scope='session')
def sample_patient_id(supabase_client):
    """Get an existing patient ID from seed data."""
    result = supabase_client.table('patients').select('id').limit(1).execute()
    assert result.data, 'No patients in DB'
    return result.data[0]['id']


@pytest.fixture(scope='session')
def sample_service_id(supabase_client):
    """Get an existing service ID from seed data."""
    result = supabase_client.table('services').select('id').limit(1).execute()
    assert result.data, 'No services in DB'
    return result.data[0]['id']


@pytest.fixture(scope='function')
def temp_patient(supabase_client):
    """Create a temporary patient for testing, clean up after."""
    unique = uuid.uuid4().hex[:6]
    data = {
        'first_name': 'טסט',
        'last_name': f'בדיקה{unique}',
        'id_number': f'{900000000 + hash(unique) % 99999}',
        'phone': f'050-{7000000 + hash(unique) % 999999}',
        'email': f'test_{unique}@example.com',
        'gender': 'male',
    }
    result = supabase_client.table('patients').insert(data).execute()
    patient = result.data[0]
    yield patient
    try:
        supabase_client.table('patients').delete().eq('id', patient['id']).execute()
    except Exception:
        pass


@pytest.fixture(scope='function')
def temp_service(supabase_client):
    """Create a temporary service for testing, clean up after."""
    unique = uuid.uuid4().hex[:6]
    data = {
        'name': f'שירות בדיקה {unique}',
        'description': 'שירות לצורך בדיקות',
        'price': 100.00,
        'duration_minutes': 15,
        'is_active': True,
    }
    result = supabase_client.table('services').insert(data).execute()
    service = result.data[0]
    yield service
    try:
        supabase_client.table('services').delete().eq('id', service['id']).execute()
    except Exception:
        pass
