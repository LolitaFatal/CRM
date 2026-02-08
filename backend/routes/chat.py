from flask import Blueprint, render_template, request, jsonify
from backend.middleware.auth_middleware import login_required, role_required
from backend.services import chat_service

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/chat')
@login_required
@role_required('doctor')
def index():
    return render_template('chat/index.html')


@chat_bp.route('/api/chat', methods=['POST'])
@login_required
@role_required('doctor')
def send_message():
    data = request.get_json()
    question = data.get('question', '')

    result = chat_service.chat(question)
    return jsonify({
        'success': True,
        'data': result,
    })
