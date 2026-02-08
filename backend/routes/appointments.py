from flask import Blueprint, render_template, request, jsonify
from backend.middleware.auth_middleware import login_required
from backend.services import appointment_service, catalog_service, patient_service

appointments_bp = Blueprint('appointments', __name__)


@appointments_bp.route('/appointments')
@login_required
def list_appointments():
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    page = int(request.args.get('page', 1))
    result = appointment_service.get_appointments(
        search=search, status_filter=status_filter, page=page
    )
    services = catalog_service.get_all_services()
    patients = patient_service.get_patients(limit=100)['data']
    return render_template('appointments/list.html',
                           **result, search=search, status_filter=status_filter,
                           services=services, patients_list=patients)


@appointments_bp.route('/api/appointments', methods=['POST'])
@login_required
def create():
    data = request.get_json()
    appointment = appointment_service.create_appointment(data)
    if appointment:
        return jsonify({'success': True, 'data': appointment})
    return jsonify({'success': False, 'error': 'שגיאה ביצירת תור'}), 400


@appointments_bp.route('/api/appointments/<appointment_id>', methods=['PUT'])
@login_required
def update(appointment_id):
    data = request.get_json()
    appointment = appointment_service.update_appointment(appointment_id, data)
    if appointment:
        return jsonify({'success': True, 'data': appointment})
    return jsonify({'success': False, 'error': 'שגיאה בעדכון תור'}), 400


@appointments_bp.route('/api/appointments/<appointment_id>', methods=['DELETE'])
@login_required
def delete(appointment_id):
    try:
        appointment_service.delete_appointment(appointment_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
