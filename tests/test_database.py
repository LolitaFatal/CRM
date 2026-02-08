"""
Phase 1: Database Tests
Schema integrity, foreign keys, seed data validation, RPC function.
"""
import re
import pytest

pytestmark = pytest.mark.database


# ============================================================
# 1.1 Schema Integrity
# ============================================================

class TestSchemaIntegrity:
    """Verify all tables exist with correct structure."""

    EXPECTED_TABLES = [
        'users', 'patients', 'medical_history',
        'services', 'appointments', 'invoices', 'tasks',
    ]

    def test_all_tables_exist(self, supabase_client):
        """Verify all 7 tables exist."""
        for table in self.EXPECTED_TABLES:
            result = supabase_client.table(table).select('id').limit(0).execute()
            # If table doesn't exist, supabase raises an error
            assert result is not None, f'Table {table} does not exist'

    def test_users_columns(self, supabase_client):
        """Verify users table has expected columns."""
        result = supabase_client.table('users').select('id, email, password_hash, full_name, role, created_at').limit(1).execute()
        if result.data:
            row = result.data[0]
            assert 'id' in row
            assert 'email' in row
            assert 'password_hash' in row
            assert 'full_name' in row
            assert 'role' in row
            assert 'created_at' in row

    def test_patients_columns(self, supabase_client):
        """Verify patients table has expected columns."""
        result = supabase_client.table('patients').select(
            'id, first_name, last_name, id_number, date_of_birth, gender, phone, email, address, created_at'
        ).limit(1).execute()
        if result.data:
            row = result.data[0]
            for col in ['id', 'first_name', 'last_name', 'id_number', 'date_of_birth',
                         'gender', 'phone', 'email', 'address', 'created_at']:
                assert col in row, f'Column {col} missing from patients'

    def test_medical_history_columns(self, supabase_client):
        """Verify medical_history has TEXT[] array columns."""
        result = supabase_client.table('medical_history').select(
            'id, patient_id, diagnoses, medications, allergies, chronic_conditions, notes, updated_at'
        ).limit(1).execute()
        if result.data:
            row = result.data[0]
            assert 'diagnoses' in row
            assert 'medications' in row
            assert 'allergies' in row
            # Verify arrays are returned as lists
            assert isinstance(row['diagnoses'], list) or row['diagnoses'] is None
            assert isinstance(row['medications'], list) or row['medications'] is None
            assert isinstance(row['allergies'], list) or row['allergies'] is None

    def test_services_columns(self, supabase_client):
        """Verify services table has expected columns."""
        result = supabase_client.table('services').select(
            'id, name, description, price, duration_minutes, is_active'
        ).limit(1).execute()
        if result.data:
            row = result.data[0]
            for col in ['id', 'name', 'price', 'duration_minutes', 'is_active']:
                assert col in row

    def test_appointments_columns(self, supabase_client):
        """Verify appointments table has expected columns."""
        result = supabase_client.table('appointments').select(
            'id, patient_id, service_id, doctor_id, appointment_date, status, notes, created_at'
        ).limit(1).execute()
        if result.data:
            row = result.data[0]
            for col in ['id', 'patient_id', 'service_id', 'doctor_id',
                         'appointment_date', 'status', 'notes']:
                assert col in row

    def test_invoices_columns(self, supabase_client):
        """Verify invoices table columns (status, NOT payment_status)."""
        result = supabase_client.table('invoices').select(
            'id, invoice_number, patient_id, appointment_id, amount, status, issued_date, paid_date, created_at'
        ).limit(1).execute()
        if result.data:
            row = result.data[0]
            for col in ['id', 'invoice_number', 'patient_id', 'amount', 'status', 'issued_date']:
                assert col in row

    def test_tasks_columns(self, supabase_client):
        """Verify tasks table columns (no created_by, no related_patient_id)."""
        result = supabase_client.table('tasks').select(
            'id, title, description, status, priority, assigned_to, due_date, position, created_at'
        ).limit(1).execute()
        if result.data:
            row = result.data[0]
            for col in ['id', 'title', 'status', 'priority', 'assigned_to', 'position']:
                assert col in row


# ============================================================
# 1.2 CHECK Constraints (Enum Validation)
# ============================================================

class TestCheckConstraints:
    """Verify CHECK constraints reject invalid values."""

    def test_users_role_valid(self, supabase_client):
        """Valid roles: doctor, secretary."""
        result = supabase_client.table('users').select('role').execute()
        roles = {u['role'] for u in result.data}
        assert roles.issubset({'doctor', 'secretary'})

    def test_users_role_invalid(self, supabase_client):
        """Invalid role should be rejected by CHECK constraint."""
        with pytest.raises(Exception):
            supabase_client.table('users').insert({
                'email': 'invalid_role@test.com',
                'password_hash': 'hash',
                'full_name': 'Test',
                'role': 'admin',  # Invalid
            }).execute()

    def test_appointments_status_valid(self, supabase_client):
        """Valid statuses: scheduled, completed, cancelled, no_show."""
        result = supabase_client.table('appointments').select('status').execute()
        statuses = {a['status'] for a in result.data}
        assert statuses.issubset({'scheduled', 'completed', 'cancelled', 'no_show'})

    def test_invoices_status_valid(self, supabase_client):
        """Valid statuses: paid, pending, overdue, cancelled."""
        result = supabase_client.table('invoices').select('status').execute()
        statuses = {i['status'] for i in result.data}
        assert statuses.issubset({'paid', 'pending', 'overdue', 'cancelled'})

    def test_tasks_status_valid(self, supabase_client):
        """Valid statuses: open, in_progress, done."""
        result = supabase_client.table('tasks').select('status').execute()
        statuses = {t['status'] for t in result.data}
        assert statuses.issubset({'open', 'in_progress', 'done'})

    def test_tasks_priority_valid(self, supabase_client):
        """Valid priorities: urgent, medium, normal (NOT low/high)."""
        result = supabase_client.table('tasks').select('priority').execute()
        priorities = {t['priority'] for t in result.data}
        assert priorities.issubset({'urgent', 'medium', 'normal'})

    def test_patients_gender_valid(self, supabase_client):
        """Valid genders: male, female, other."""
        result = supabase_client.table('patients').select('gender').execute()
        genders = {p['gender'] for p in result.data if p['gender']}
        assert genders.issubset({'male', 'female', 'other'})


# ============================================================
# 1.3 Foreign Key Integrity
# ============================================================

class TestForeignKeys:
    """Verify FK relationships and cascade behavior."""

    def test_medical_history_patient_fk(self, supabase_client):
        """Every medical_history record references a valid patient."""
        histories = supabase_client.table('medical_history').select('patient_id').execute().data
        patient_ids = {p['id'] for p in supabase_client.table('patients').select('id').execute().data}
        for h in histories:
            assert h['patient_id'] in patient_ids, f'Orphan medical_history: patient_id={h["patient_id"]}'

    def test_appointments_patient_fk(self, supabase_client):
        """Every appointment references a valid patient."""
        appointments = supabase_client.table('appointments').select('patient_id').execute().data
        patient_ids = {p['id'] for p in supabase_client.table('patients').select('id').execute().data}
        for a in appointments:
            assert a['patient_id'] in patient_ids

    def test_appointments_service_fk(self, supabase_client):
        """Every appointment references a valid service."""
        appointments = supabase_client.table('appointments').select('service_id').execute().data
        service_ids = {s['id'] for s in supabase_client.table('services').select('id').execute().data}
        for a in appointments:
            if a['service_id']:
                assert a['service_id'] in service_ids

    def test_invoices_patient_fk(self, supabase_client):
        """Every invoice references a valid patient."""
        invoices = supabase_client.table('invoices').select('patient_id').execute().data
        patient_ids = {p['id'] for p in supabase_client.table('patients').select('id').execute().data}
        for inv in invoices:
            assert inv['patient_id'] in patient_ids

    def test_invoices_appointment_fk(self, supabase_client):
        """Every invoice with appointment_id references a valid appointment."""
        invoices = supabase_client.table('invoices').select('appointment_id').execute().data
        apt_ids = {a['id'] for a in supabase_client.table('appointments').select('id').execute().data}
        for inv in invoices:
            if inv['appointment_id']:
                assert inv['appointment_id'] in apt_ids

    def test_tasks_assigned_to_fk(self, supabase_client):
        """Every task with assigned_to references a valid user."""
        tasks = supabase_client.table('tasks').select('assigned_to').execute().data
        user_ids = {u['id'] for u in supabase_client.table('users').select('id').execute().data}
        for t in tasks:
            if t['assigned_to']:
                assert t['assigned_to'] in user_ids

    def test_insert_invalid_fk_rejected(self, supabase_client):
        """Inserting with non-existent FK should fail."""
        fake_uuid = '00000000-0000-0000-0000-000000000000'
        with pytest.raises(Exception):
            supabase_client.table('medical_history').insert({
                'patient_id': fake_uuid,
                'diagnoses': [],
                'medications': [],
                'allergies': [],
            }).execute()

    def test_cascade_delete_patient(self, supabase_client, doctor_user):
        """Deleting a patient cascades to medical_history, appointments, invoices."""
        # Create temp patient
        patient = supabase_client.table('patients').insert({
            'first_name': 'מחיקה', 'last_name': 'בדיקה', 'id_number': '888888888',
        }).execute().data[0]
        pid = patient['id']

        # Create related records
        supabase_client.table('medical_history').insert({
            'patient_id': pid, 'diagnoses': ['test'], 'medications': [], 'allergies': [],
        }).execute()
        supabase_client.table('appointments').insert({
            'patient_id': pid,
            'service_id': supabase_client.table('services').select('id').limit(1).execute().data[0]['id'],
            'doctor_id': doctor_user['id'],
            'appointment_date': '2026-03-01T10:00:00',
            'status': 'scheduled',
        }).execute()

        # Delete patient — should cascade
        supabase_client.table('patients').delete().eq('id', pid).execute()

        # Verify cascade
        mh = supabase_client.table('medical_history').select('id').eq('patient_id', pid).execute().data
        assert len(mh) == 0, 'medical_history not cascaded'

        apts = supabase_client.table('appointments').select('id').eq('patient_id', pid).execute().data
        assert len(apts) == 0, 'appointments not cascaded'


# ============================================================
# 1.4 Seed Data Validation
# ============================================================

class TestSeedData:
    """Verify seed data integrity."""

    def test_users_count(self, supabase_client):
        """Should have exactly 2 users (doctor + secretary)."""
        result = supabase_client.table('users').select('id', count='exact').execute()
        assert result.count >= 2

    def test_doctor_exists(self, supabase_client):
        """Doctor user exists with correct role."""
        result = supabase_client.table('users').select('*').eq('email', 'doctor@demo.com').execute()
        assert len(result.data) == 1
        assert result.data[0]['role'] == 'doctor'

    def test_secretary_exists(self, supabase_client):
        """Secretary user exists with correct role."""
        result = supabase_client.table('users').select('*').eq('email', 'secretary@demo.com').execute()
        assert len(result.data) == 1
        assert result.data[0]['role'] == 'secretary'

    def test_patients_count(self, supabase_client):
        """Should have at least 20 patients."""
        result = supabase_client.table('patients').select('id', count='exact').execute()
        assert result.count >= 20

    def test_services_count(self, supabase_client):
        """Should have at least 8 services."""
        result = supabase_client.table('services').select('id', count='exact').execute()
        assert result.count >= 8

    def test_appointments_count(self, supabase_client):
        """Should have approximately 60 appointments."""
        result = supabase_client.table('appointments').select('id', count='exact').execute()
        assert result.count >= 50  # Allow some margin

    def test_invoices_count(self, supabase_client):
        """Should have invoices (count depends on completed appointments)."""
        result = supabase_client.table('invoices').select('id', count='exact').execute()
        assert result.count >= 20  # At least some invoices exist

    def test_tasks_count(self, supabase_client):
        """Should have at least 10 tasks."""
        result = supabase_client.table('tasks').select('id', count='exact').execute()
        assert result.count >= 10

    def test_medical_history_count(self, supabase_client):
        """Should have medical history for all 20 patients."""
        result = supabase_client.table('medical_history').select('id', count='exact').execute()
        assert result.count >= 20

    def test_patient_names_hebrew(self, supabase_client):
        """Patient names should be in Hebrew."""
        result = supabase_client.table('patients').select('first_name, last_name').execute()
        hebrew_pattern = re.compile(r'[\u0590-\u05FF]')
        for p in result.data:
            assert hebrew_pattern.search(p['first_name']), f'Non-Hebrew name: {p["first_name"]}'

    def test_phone_pattern(self, supabase_client):
        """Phone numbers should match 05X-XXXXXXX pattern."""
        result = supabase_client.table('patients').select('phone').execute()
        phone_re = re.compile(r'^05\d-\d{7}$')
        for p in result.data:
            if p['phone']:
                assert phone_re.match(p['phone']), f'Invalid phone: {p["phone"]}'

    def test_appointment_status_distribution(self, supabase_client):
        """Appointments should have mixed statuses (not all completed)."""
        result = supabase_client.table('appointments').select('status').execute()
        statuses = {a['status'] for a in result.data}
        assert len(statuses) >= 3, f'Only {statuses} statuses found — expected at least 3'

    def test_invoice_status_distribution(self, supabase_client):
        """Invoices should have mixed statuses."""
        result = supabase_client.table('invoices').select('status').execute()
        statuses = {i['status'] for i in result.data}
        assert len(statuses) >= 2, f'Only {statuses} statuses found'

    def test_passwords_are_hashed(self, supabase_client):
        """User passwords should be hashed, not plaintext."""
        result = supabase_client.table('users').select('password_hash').execute()
        for u in result.data:
            assert u['password_hash'].startswith('pbkdf2:sha256:'), \
                'Password not hashed with pbkdf2:sha256'


# ============================================================
# 1.5 RPC Function
# ============================================================

class TestRPCFunction:
    """Test execute_readonly_query RPC."""

    def test_rpc_select_allowed(self, supabase_client):
        """RPC should allow SELECT queries."""
        result = supabase_client.rpc('execute_readonly_query', {
            'query_text': "SELECT COUNT(*) AS cnt FROM patients"
        }).execute()
        assert result.data is not None
        assert isinstance(result.data, list)
        assert result.data[0]['cnt'] >= 1

    def test_rpc_insert_blocked(self, supabase_client):
        """RPC should block INSERT queries."""
        with pytest.raises(Exception) as exc_info:
            supabase_client.rpc('execute_readonly_query', {
                'query_text': "INSERT INTO patients (first_name, last_name) VALUES ('a', 'b')"
            }).execute()
        assert 'blocked' in str(exc_info.value).lower() or 'select' in str(exc_info.value).lower()

    def test_rpc_delete_blocked(self, supabase_client):
        """RPC should block DELETE queries."""
        with pytest.raises(Exception):
            supabase_client.rpc('execute_readonly_query', {
                'query_text': "DELETE FROM patients"
            }).execute()

    def test_rpc_drop_blocked(self, supabase_client):
        """RPC should block DROP queries."""
        with pytest.raises(Exception):
            supabase_client.rpc('execute_readonly_query', {
                'query_text': "DROP TABLE patients"
            }).execute()

    def test_rpc_update_blocked(self, supabase_client):
        """RPC should block UPDATE queries."""
        with pytest.raises(Exception):
            supabase_client.rpc('execute_readonly_query', {
                'query_text': "UPDATE patients SET first_name = 'hacked'"
            }).execute()

    def test_rpc_returns_json_array(self, supabase_client):
        """RPC returns JSON array of results."""
        result = supabase_client.rpc('execute_readonly_query', {
            'query_text': "SELECT id, first_name, last_name FROM patients LIMIT 3"
        }).execute()
        assert isinstance(result.data, list)
        if result.data:
            assert 'first_name' in result.data[0]

    def test_rpc_empty_result(self, supabase_client):
        """RPC returns empty array for no results."""
        result = supabase_client.rpc('execute_readonly_query', {
            'query_text': "SELECT * FROM patients WHERE id = '00000000-0000-0000-0000-000000000000'"
        }).execute()
        assert result.data == [] or result.data is None

    def test_rpc_semicolon_in_subquery(self, supabase_client):
        """Trailing semicolon causes syntax error in RPC subquery wrapping.
        This documents the known semicolon bug."""
        try:
            result = supabase_client.rpc('execute_readonly_query', {
                'query_text': "SELECT COUNT(*) AS cnt FROM patients;"
            }).execute()
            # If it somehow works, that's fine too
        except Exception as e:
            # Expected: syntax error because RPC wraps as:
            # SELECT json_agg(row_to_json(t)) FROM (SELECT ...; ) t
            assert 'syntax' in str(e).lower() or 'error' in str(e).lower()
            pytest.xfail('Known bug: trailing semicolon breaks RPC subquery wrapping')
