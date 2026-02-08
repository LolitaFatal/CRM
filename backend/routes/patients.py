from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session
from backend.middleware.auth_middleware import login_required, role_required
from backend.services import patient_service

patients_bp = Blueprint('patients', __name__)


@patients_bp.route('/patients')
@login_required
def list_patients():
    search = request.args.get('search', '')
    page = int(request.args.get('page', 1))
    result = patient_service.get_patients(search=search, page=page)
    return render_template('patients/list.html', **result, search=search)


@patients_bp.route('/patients/<patient_id>')
@login_required
def detail(patient_id):
    patient = patient_service.get_patient(patient_id)
    if not patient:
        flash('המטופל לא נמצא', 'danger')
        return redirect(url_for('patients.list_patients'))

    medical_history = None
    if session.get('user_role') == 'doctor':
        medical_history = patient_service.get_patient_medical_history(patient_id)

    appointments = patient_service.get_patient_appointments(patient_id)
    invoices = patient_service.get_patient_invoices(patient_id)

    return render_template('patients/detail.html',
                           patient=patient,
                           medical_history=medical_history,
                           appointments=appointments,
                           invoices=invoices)


@patients_bp.route('/api/patients', methods=['POST'])
@login_required
def create():
    data = request.get_json()
    patient = patient_service.create_patient(data)
    if patient:
        return jsonify({'success': True, 'data': patient})
    return jsonify({'success': False, 'error': 'שגיאה ביצירת מטופל'}), 400


@patients_bp.route('/api/patients/<patient_id>', methods=['PUT'])
@login_required
def update(patient_id):
    data = request.get_json()
    patient = patient_service.update_patient(patient_id, data)
    if patient:
        return jsonify({'success': True, 'data': patient})
    return jsonify({'success': False, 'error': 'שגיאה בעדכון מטופל'}), 400


@patients_bp.route('/api/patients/<patient_id>', methods=['DELETE'])
@login_required
def delete(patient_id):
    try:
        patient_service.delete_patient(patient_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@patients_bp.route('/api/patients/<patient_id>/medical-history', methods=['PUT'])
@login_required
@role_required('doctor')
def update_medical(patient_id):
    data = request.get_json()
    result = patient_service.update_medical_history(patient_id, data)
    if result:
        return jsonify({'success': True, 'data': result})
    return jsonify({'success': False, 'error': 'שגיאה בעדכון היסטוריה רפואית'}), 400
