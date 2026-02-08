from flask import Blueprint, render_template, request, jsonify
from backend.middleware.auth_middleware import login_required
from backend.services import invoice_service, patient_service, catalog_service

invoices_bp = Blueprint('invoices', __name__)


@invoices_bp.route('/invoices')
@login_required
def list_invoices():
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    page = int(request.args.get('page', 1))
    result = invoice_service.get_invoices(
        search=search, status_filter=status_filter, page=page
    )
    patients = patient_service.get_patients(limit=100)['data']
    services = catalog_service.get_all_services()
    return render_template('invoices/list.html',
                           **result, search=search, status_filter=status_filter,
                           patients_list=patients, services=services)


@invoices_bp.route('/api/invoices', methods=['POST'])
@login_required
def create():
    data = request.get_json()
    invoice = invoice_service.create_invoice(data)
    if invoice:
        return jsonify({'success': True, 'data': invoice})
    return jsonify({'success': False, 'error': 'שגיאה ביצירת חשבונית'}), 400


@invoices_bp.route('/api/invoices/<invoice_id>', methods=['PUT'])
@login_required
def update(invoice_id):
    data = request.get_json()
    invoice = invoice_service.update_invoice(invoice_id, data)
    if invoice:
        return jsonify({'success': True, 'data': invoice})
    return jsonify({'success': False, 'error': 'שגיאה בעדכון חשבונית'}), 400


@invoices_bp.route('/api/invoices/<invoice_id>/pay', methods=['POST'])
@login_required
def mark_paid(invoice_id):
    invoice = invoice_service.mark_as_paid(invoice_id)
    if invoice:
        return jsonify({'success': True, 'data': invoice})
    return jsonify({'success': False, 'error': 'שגיאה בסימון תשלום'}), 400


@invoices_bp.route('/api/invoices/<invoice_id>', methods=['DELETE'])
@login_required
def delete(invoice_id):
    try:
        invoice_service.delete_invoice(invoice_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
