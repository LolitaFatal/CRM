from datetime import datetime, timedelta
from backend.extensions import get_supabase


def get_total_patients():
    supabase = get_supabase()
    result = supabase.table('patients').select('id', count='exact').execute()
    return result.count or 0


def get_monthly_appointments():
    supabase = get_supabase()
    now = datetime.now()
    start = now.replace(day=1, hour=0, minute=0, second=0).isoformat()
    end = now.isoformat()

    result = supabase.table('appointments').select('id', count='exact') \
        .gte('appointment_date', start) \
        .lte('appointment_date', end) \
        .execute()
    return result.count or 0


def get_monthly_revenue():
    supabase = get_supabase()
    now = datetime.now()
    start = now.replace(day=1, hour=0, minute=0, second=0).isoformat()

    result = supabase.table('invoices').select('amount') \
        .eq('status', 'paid') \
        .gte('issued_date', start[:10]) \
        .execute()

    return sum(float(inv['amount']) for inv in (result.data or []))


def get_pending_payments():
    supabase = get_supabase()
    result = supabase.table('invoices').select('amount') \
        .in_('status', ['pending', 'overdue']) \
        .execute()

    data = result.data or []
    return {
        'count': len(data),
        'total': sum(float(inv['amount']) for inv in data),
    }


def get_revenue_by_month(months=6):
    supabase = get_supabase()
    now = datetime.now()
    start_date = (now - timedelta(days=months * 30)).replace(day=1)

    result = supabase.table('invoices').select('amount, issued_date') \
        .eq('status', 'paid') \
        .gte('issued_date', start_date.strftime('%Y-%m-%d')) \
        .execute()

    monthly = {}
    for inv in (result.data or []):
        month_key = inv['issued_date'][:7]  # YYYY-MM
        monthly[month_key] = monthly.get(month_key, 0) + float(inv['amount'])

    labels = []
    values = []
    for i in range(months):
        d = now - timedelta(days=(months - 1 - i) * 30)
        key = d.strftime('%Y-%m')
        month_names = {
            '01': 'ינואר', '02': 'פברואר', '03': 'מרץ',
            '04': 'אפריל', '05': 'מאי', '06': 'יוני',
            '07': 'יולי', '08': 'אוגוסט', '09': 'ספטמבר',
            '10': 'אוקטובר', '11': 'נובמבר', '12': 'דצמבר',
        }
        labels.append(month_names.get(key[5:7], key[5:7]))
        values.append(monthly.get(key, 0))

    return {'labels': labels, 'values': values}


def get_appointment_status_distribution():
    supabase = get_supabase()
    result = supabase.table('appointments').select('status').execute()

    counts = {'completed': 0, 'scheduled': 0, 'cancelled': 0, 'no_show': 0}
    for apt in (result.data or []):
        status = apt['status']
        if status in counts:
            counts[status] += 1

    return counts
