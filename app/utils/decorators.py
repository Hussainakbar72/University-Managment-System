from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user

def role_required(*roles):
    """
    Decorator to restrict view access to users with specified role(s).
    Roles can be strings like 'ADMIN', 'TEACHER', 'STUDENT'.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login'))
            
            user_roles = [r.name.upper() for r in [ur.role for ur in current_user.roles if ur.role]]
            required = [r.upper() for r in roles]
            
            # Super Admin override
            if 'ADMIN' in user_roles:
                return f(*args, **kwargs)
                
            if not any(r in user_roles for r in required):
                flash('You do not have permission to access this resource.', 'danger')
                abort(403)
                
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    return role_required('ADMIN')(f)

def teacher_required(f):
    return role_required('TEACHER', 'ADMIN')(f)

def student_required(f):
    return role_required('STUDENT', 'ADMIN')(f)
