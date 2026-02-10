from flask import Flask, jsonify
from flask_cors import CORS


def create_app():
    app = Flask(__name__)

    app.config.from_object('backend.config.Config')

    frontend_url = app.config.get('FRONTEND_URL', 'http://localhost:5173')
    allowed_origins = [origin.strip() for origin in frontend_url.split(',') if origin.strip()]
    CORS(app, origins=allowed_origins, supports_credentials=True)

    from backend.routes import register_blueprints
    register_blueprints(app)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({'success': False, 'error': 'לא נמצא'}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({'success': False, 'error': 'שגיאת שרת פנימית'}), 500

    return app
