from backend.extensions import get_supabase


def get_services(search='', page=1, limit=10):
    supabase = get_supabase()
    query = supabase.table('services').select('*', count='exact')

    if search:
        query = query.or_(f'name.ilike.%{search}%,description.ilike.%{search}%')

    query = query.order('name')
    offset = (page - 1) * limit
    query = query.range(offset, offset + limit - 1)

    result = query.execute()
    return {
        'data': result.data or [],
        'total': result.count or 0,
        'page': page,
        'limit': limit,
    }


def get_all_services():
    supabase = get_supabase()
    result = supabase.table('services').select('*').eq('is_active', True).order('name').execute()
    return result.data or []


def get_service(service_id: str):
    supabase = get_supabase()
    result = supabase.table('services').select('*').eq('id', service_id).execute()
    return result.data[0] if result.data else None


def create_service(data: dict):
    supabase = get_supabase()
    result = supabase.table('services').insert(data).execute()
    return result.data[0] if result.data else None


def update_service(service_id: str, data: dict):
    supabase = get_supabase()
    result = supabase.table('services').update(data).eq('id', service_id).execute()
    return result.data[0] if result.data else None


def delete_service(service_id: str):
    supabase = get_supabase()
    supabase.table('services').delete().eq('id', service_id).execute()
