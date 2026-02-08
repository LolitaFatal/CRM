from supabase import create_client, Client
from flask import current_app

_supabase_client: Client | None = None


def get_supabase() -> Client:
    global _supabase_client
    if _supabase_client is None:
        url = current_app.config['SUPABASE_URL']
        key = current_app.config['SUPABASE_KEY']
        if not url or not key:
            raise RuntimeError('SUPABASE_URL and SUPABASE_KEY must be set')
        _supabase_client = create_client(url, key)
    return _supabase_client
