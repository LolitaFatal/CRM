from flask import Blueprint, render_template, jsonify, session
from backend.middleware.auth_middleware import login_required
from backend.services import dashboard_service

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/dashboard')
@login_required
def index():
    total_patients = dashboard_service.get_total_patients()
    monthly_appointments = dashboard_service.get_monthly_appointments()
    monthly_revenue = dashboard_service.get_monthly_revenue()
    pending = dashboard_service.get_pending_payments()

    churn_patients = []
    if session.get('user_role') == 'doctor':
        try:
            from backend.services.churn_service import get_all_churn_scores
            churn_patients = get_all_churn_scores()[:5]
        except Exception:
            churn_patients = []

    return render_template('dashboard/index.html',
                           total_patients=total_patients,
                           monthly_appointments=monthly_appointments,
                           monthly_revenue=monthly_revenue,
                           pending_count=pending['count'],
                           pending_total=pending['total'],
                           churn_patients=churn_patients)


@dashboard_bp.route('/api/dashboard/revenue-chart')
@login_required
def revenue_chart():
    data = dashboard_service.get_revenue_by_month(6)
    return jsonify({'success': True, 'data': data})


@dashboard_bp.route('/api/dashboard/appointment-chart')
@login_required
def appointment_chart():
    data = dashboard_service.get_appointment_status_distribution()
    return jsonify({'success': True, 'data': data})
