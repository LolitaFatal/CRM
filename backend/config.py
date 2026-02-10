import os
import sys
from dotenv import load_dotenv

load_dotenv()

_is_production = bool(os.environ.get('RAILWAY_ENVIRONMENT'))


def _require_env(name: str) -> str:
    value = os.environ.get(name, '')
    if not value:
        print(f"FATAL: Required environment variable {name} is not set", file=sys.stderr)
        sys.exit(1)
    return value


def _require_env_in_prod(name: str, dev_default: str) -> str:
    value = os.environ.get(name, '')
    if not value:
        if _is_production:
            print(f"FATAL: {name} must be set in production", file=sys.stderr)
            sys.exit(1)
        return dev_default
    return value


class Config:
    SECRET_KEY = _require_env_in_prod('FLASK_SECRET_KEY', 'dev-secret-key-change-me')
    JWT_SECRET_KEY = _require_env_in_prod('JWT_SECRET_KEY', 'dev-jwt-secret-change-me')
    SUPABASE_URL = _require_env('SUPABASE_URL')
    SUPABASE_KEY = _require_env('SUPABASE_KEY')
    SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
