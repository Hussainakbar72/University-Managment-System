import os
from flask import Flask, render_template
from config import config
from app.extensions import db, migrate, login_manager, csrf

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.academic import academic_bp
    from app.routes.users_mgmt import users_mgmt_bp
    from app.routes.students_mgmt import students_mgmt_bp
    from app.routes.instructors_mgmt import instructors_mgmt_bp
    from app.routes.enrollment_mgmt import enrollment_mgmt_bp
    from app.routes.exams_mgmt import exams_mgmt_bp
    from app.routes.finance_mgmt import finance_mgmt_bp
    from app.routes.services_mgmt import services_mgmt_bp
    from app.routes.reports import reports_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(academic_bp)
    app.register_blueprint(users_mgmt_bp)
    app.register_blueprint(students_mgmt_bp)
    app.register_blueprint(instructors_mgmt_bp)
    app.register_blueprint(enrollment_mgmt_bp)
    app.register_blueprint(exams_mgmt_bp)
    app.register_blueprint(finance_mgmt_bp)
    app.register_blueprint(services_mgmt_bp)
    app.register_blueprint(reports_bp)

    # Register Error Handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template('errors/500.html'), 500

    # Context processors
    @app.context_processor
    def inject_global_vars():
        from datetime import datetime
        return {
            'now': datetime.utcnow(),
            'app_name': 'University Management System'
        }

    return app
