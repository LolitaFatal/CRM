import logging

from flask import Blueprint, jsonify

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)


@health_bp.route('/healthz')
def healthcheck():
    return jsonify({'status': 'ok'}), 200


@health_bp.route('/readyz')
def readiness():
    try:
        from backend.extensions import get_supabase
        client = get_supabase()
        client.table('users').select('id').limit(1).execute()
        return jsonify({'status': 'ready', 'database': 'connected'}), 200
    except Exception as e:
        logger.error('Readiness check failed: %s', e)
        return jsonify({'status': 'not_ready'}), 503
