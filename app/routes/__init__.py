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

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'academic_bp',
    'users_mgmt_bp',
    'students_mgmt_bp',
    'instructors_mgmt_bp',
    'enrollment_mgmt_bp',
    'exams_mgmt_bp',
    'finance_mgmt_bp',
    'services_mgmt_bp',
    'reports_bp'
]
