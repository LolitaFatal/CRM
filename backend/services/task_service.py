from backend.extensions import get_supabase


def get_tasks_grouped():
    supabase = get_supabase()
    result = supabase.table('tasks').select('*, users!tasks_assigned_to_fkey(full_name)') \
        .order('position') \
        .execute()

    grouped = {
        'open': [],
        'in_progress': [],
        'done': [],
    }
    for task in (result.data or []):
        status = task.get('status', 'open')
        if status in grouped:
            grouped[status].append(task)

    return grouped


def get_task(task_id: str):
    supabase = get_supabase()
    result = supabase.table('tasks').select('*').eq('id', task_id).execute()
    return result.data[0] if result.data else None


def create_task(data: dict):
    supabase = get_supabase()
    result = supabase.table('tasks').insert(data).execute()
    return result.data[0] if result.data else None


def update_task(task_id: str, data: dict):
    supabase = get_supabase()
    result = supabase.table('tasks').update(data).eq('id', task_id).execute()
    return result.data[0] if result.data else None


def update_task_status(task_id: str, new_status: str, position: int = 0):
    supabase = get_supabase()
    result = supabase.table('tasks').update({
        'status': new_status,
        'position': position,
    }).eq('id', task_id).execute()
    return result.data[0] if result.data else None


def delete_task(task_id: str):
    supabase = get_supabase()
    supabase.table('tasks').delete().eq('id', task_id).execute()


def get_users():
    supabase = get_supabase()
    result = supabase.table('users').select('id, full_name, role').execute()
    return result.data or []
