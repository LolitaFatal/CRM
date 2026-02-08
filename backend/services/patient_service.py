from backend.extensions import get_supabase


def get_patients(search='', page=1, limit=10):
    supabase = get_supabase()
    query = supabase.table('patients').select('*', count='exact')

    if search:
        query = query.or_(f'first_name.ilike.%{search}%,last_name.ilike.%{search}%,phone.ilike.%{search}%,id_number.ilike.%{search}%')

    query = query.order('created_at', desc=True)
    offset = (page - 1) * limit
    query = query.range(offset, offset + limit - 1)

    result = query.execute()
    return {
        'data': result.data or [],
        'total': result.count or 0,
        'page': page,
        'limit': limit,
    }


def get_patient(patient_id: str):
    supabase = get_supabase()
    result = supabase.table('patients').select('*').eq('id', patient_id).execute()
    return result.data[0] if result.data else None


def get_patient_medical_history(patient_id: str):
    supabase = get_supabase()
    result = supabase.table('medical_history').select('*').eq('patient_id', patient_id).execute()
    return result.data[0] if result.data else None


def get_patient_appointments(patient_id: str):
    supabase = get_supabase()
    result = supabase.table('appointments').select('*, services(name)') \
        .eq('patient_id', patient_id) \
        .order('appointment_date', desc=True) \
        .execute()
    return result.data or []


def get_patient_invoices(patient_id: str):
    supabase = get_supabase()
    result = supabase.table('invoices').select('*') \
        .eq('patient_id', patient_id) \
        .order('issued_date', desc=True) \
        .execute()
    return result.data or []


def create_patient(data: dict):
    supabase = get_supabase()
    result = supabase.table('patients').insert(data).execute()
    return result.data[0] if result.data else None


def update_patient(patient_id: str, data: dict):
    supabase = get_supabase()
    result = supabase.table('patients').update(data).eq('id', patient_id).execute()
    return result.data[0] if result.data else None


def delete_patient(patient_id: str):
    supabase = get_supabase()
    supabase.table('patients').delete().eq('id', patient_id).execute()


def update_medical_history(patient_id: str, data: dict):
    supabase = get_supabase()
    existing = supabase.table('medical_history').select('id').eq('patient_id', patient_id).execute()

    record = {**data, 'patient_id': patient_id}

    if existing.data:
        result = supabase.table('medical_history').update(record).eq('patient_id', patient_id).execute()
    else:
        result = supabase.table('medical_history').insert(record).execute()

    return result.data[0] if result.data else None
