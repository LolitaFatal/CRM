import threading

from supabase import create_client, Client
from flask import current_app

_supabase_client: Client | None = None
_supabase_lock = threading.Lock()


def get_supabase() -> Client:
    global _supabase_client
    if _supabase_client is not None:
        return _supabase_client
    with _supabase_lock:
        if _supabase_client is not None:
            return _supabase_client
        url = current_app.config['SUPABASE_URL']
        key = current_app.config['SUPABASE_KEY']
        if not url or not key:
            raise RuntimeError('SUPABASE_URL and SUPABASE_KEY must be set')
        _supabase_client = create_client(url, key)
        return _supabase_client
