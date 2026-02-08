from werkzeug.security import generate_password_hash, check_password_hash
from backend.extensions import get_supabase


def hash_password(password: str) -> str:
    return generate_password_hash(password, method='pbkdf2:sha256')


def verify_password(password_hash: str, password: str) -> bool:
    return check_password_hash(password_hash, password)


def authenticate_user(email: str, password: str) -> dict | None:
    supabase = get_supabase()
    result = supabase.table('users').select('*').eq('email', email).execute()

    if not result.data:
        return None

    user = result.data[0]
    if not verify_password(user['password_hash'], password):
        return None

    return {
        'id': user['id'],
        'email': user['email'],
        'full_name': user['full_name'],
        'role': user['role'],
    }
