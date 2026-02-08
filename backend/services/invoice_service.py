from backend.extensions import get_supabase


def get_invoices(search='', status_filter='', page=1, limit=10):
    supabase = get_supabase()
    query = supabase.table('invoices').select(
        '*, patients(first_name, last_name)',
        count='exact'
    )

    if status_filter:
        query = query.eq('status', status_filter)

    query = query.order('issued_date', desc=True)
    offset = (page - 1) * limit
    query = query.range(offset, offset + limit - 1)

    result = query.execute()
    return {
        'data': result.data or [],
        'total': result.count or 0,
        'page': page,
        'limit': limit,
    }


def get_invoice(invoice_id: str):
    supabase = get_supabase()
    result = supabase.table('invoices').select(
        '*, patients(first_name, last_name)'
    ).eq('id', invoice_id).execute()
    return result.data[0] if result.data else None


def create_invoice(data: dict):
    supabase = get_supabase()
    result = supabase.table('invoices').insert(data).execute()
    return result.data[0] if result.data else None


def update_invoice(invoice_id: str, data: dict):
    supabase = get_supabase()
    result = supabase.table('invoices').update(data).eq('id', invoice_id).execute()
    return result.data[0] if result.data else None


def mark_as_paid(invoice_id: str):
    supabase = get_supabase()
    from datetime import date
    result = supabase.table('invoices').update({
        'status': 'paid',
        'paid_date': date.today().isoformat(),
    }).eq('id', invoice_id).execute()
    return result.data[0] if result.data else None


def delete_invoice(invoice_id: str):
    supabase = get_supabase()
    supabase.table('invoices').delete().eq('id', invoice_id).execute()
