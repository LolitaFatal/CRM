from flask import Blueprint, render_template, request, jsonify
from backend.middleware.auth_middleware import login_required
from backend.services import task_service

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/tasks')
@login_required
def kanban():
    grouped = task_service.get_tasks_grouped()
    users = task_service.get_users()
    return render_template('tasks/kanban.html', tasks=grouped, users=users)


@tasks_bp.route('/api/tasks', methods=['POST'])
@login_required
def create():
    data = request.get_json()
    task = task_service.create_task(data)
    if task:
        return jsonify({'success': True, 'data': task})
    return jsonify({'success': False, 'error': 'שגיאה ביצירת משימה'}), 400


@tasks_bp.route('/api/tasks/<task_id>', methods=['PUT'])
@login_required
def update(task_id):
    data = request.get_json()
    task = task_service.update_task(task_id, data)
    if task:
        return jsonify({'success': True, 'data': task})
    return jsonify({'success': False, 'error': 'שגיאה בעדכון משימה'}), 400


@tasks_bp.route('/api/tasks/<task_id>/status', methods=['PUT'])
@login_required
def update_status(task_id):
    data = request.get_json()
    new_status = data.get('status')
    position = data.get('position', 0)
    task = task_service.update_task_status(task_id, new_status, position)
    if task:
        return jsonify({'success': True, 'data': task})
    return jsonify({'success': False, 'error': 'שגיאה בעדכון סטטוס'}), 400


@tasks_bp.route('/api/tasks/<task_id>', methods=['DELETE'])
@login_required
def delete(task_id):
    try:
        task_service.delete_task(task_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400
