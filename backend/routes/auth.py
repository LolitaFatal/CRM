from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from backend.services.auth_service import authenticate_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if not email or not password:
            flash('יש למלא את כל השדות', 'warning')
            return render_template('auth/login.html')

        user = authenticate_user(email, password)
        if user is None:
            flash('אימייל או סיסמה שגויים', 'danger')
            return render_template('auth/login.html')

        session['user_id'] = user['id']
        session['user_email'] = user['email']
        session['user_name'] = user['full_name']
        session['user_role'] = user['role']

        flash(f'שלום, {user["full_name"]}!', 'success')
        return redirect(url_for('dashboard.index'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('התנתקת בהצלחה', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/')
def root():
    if 'user_id' in session:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))
