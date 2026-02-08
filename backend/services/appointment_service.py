from backend.extensions import get_supabase


def get_appointments(search='', status_filter='', page=1, limit=10):
    supabase = get_supabase()
    query = supabase.table('appointments').select(
        '*, patients(first_name, last_name), services(name)',
        count='exact'
    )

    if status_filter:
        query = query.eq('status', status_filter)

    query = query.order('appointment_date', desc=True)
    offset = (page - 1) * limit
    query = query.range(offset, offset + limit - 1)

    result = query.execute()
    return {
        'data': result.data or [],
        'total': result.count or 0,
        'page': page,
        'limit': limit,
    }


def get_appointment(appointment_id: str):
    supabase = get_supabase()
    result = supabase.table('appointments').select(
        '*, patients(first_name, last_name), services(name)'
    ).eq('id', appointment_id).execute()
    return result.data[0] if result.data else None


def create_appointment(data: dict):
    supabase = get_supabase()
    result = supabase.table('appointments').insert(data).execute()
    return result.data[0] if result.data else None


def update_appointment(appointment_id: str, data: dict):
    supabase = get_supabase()
    result = supabase.table('appointments').update(data).eq('id', appointment_id).execute()
    return result.data[0] if result.data else None


def delete_appointment(appointment_id: str):
    supabase = get_supabase()
    supabase.table('appointments').delete().eq('id', appointment_id).execute()
