from flask import Blueprint, render_template, request, jsonify
from backend.middleware.auth_middleware import login_required
from backend.services import catalog_service

services_bp = Blueprint('services', __name__)


@services_bp.route('/services')
@login_required
def list_services():
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    result = catalog_service.get_services(search=search, page=page)
    return render_template('services/list.html', **result, search=search)


@services_bp.route('/api/services', methods=['POST'])
@login_required
def create():
    data = request.get_json()
    service = catalog_service.create_service(data)
    if service:
        return jsonify({'success': True, 'data': service})
    return jsonify({'success': False, 'error': 'שגיאה ביצירת שירות'}), 400


@services_bp.route('/api/services/<service_id>', methods=['PUT'])
@login_required
def update(service_id):
    data = request.get_json()
    service = catalog_service.update_service(service_id, data)
    if service:
        return jsonify({'success': True, 'data': service})
    return jsonify({'success': False, 'error': 'שגיאה בעדכון שירות'}), 400


@services_bp.route('/api/services/<service_id>', methods=['DELETE'])
@login_required
def delete(service_id):
    try:
        catalog_service.delete_service(service_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
