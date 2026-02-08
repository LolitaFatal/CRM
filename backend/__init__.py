import os
from flask import Flask


def create_app():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    app = Flask(
        __name__,
        template_folder=os.path.join(root_dir, 'frontend', 'templates'),
        static_folder=os.path.join(root_dir, 'frontend', 'static'),
    )

    app.config.from_object('backend.config.Config')

    from backend.routes import register_blueprints
    register_blueprints(app)

    @app.errorhandler(404)
    def not_found(e):
        from flask import render_template
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def server_error(e):
        from flask import render_template
        return render_template('errors/500.html'), 500

    return app
