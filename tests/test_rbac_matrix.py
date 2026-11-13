import pytest
from app import create_app
from app.models.auth import User

@pytest.fixture(scope='module')
def dev_app():
    return create_app('development')

@pytest.fixture(scope='module')
def seeded_users(dev_app):
    users = {}
    with dev_app.app_context():
        for role, email in [
            ('ADMIN', 'admin@ums.edu'),
            ('TEACHER', 'dr.tariq@ums.edu'),
            ('STUDENT', 'ali.raza@ums.edu'),
            ('STAFF', 'staff.kamran@ums.edu')
        ]:
            u = User.query.filter_by(email=email).first()
            users[role] = str(u.id)
    return users

def get_role_client(dev_app, user_id):
    client = dev_app.test_client()
    if user_id:
        with client.session_transaction() as sess:
            sess['_user_id'] = user_id
            sess['_fresh'] = True
    return client

def test_admin_full_access(dev_app, seeded_users):
    """Admin has 200 on sensitive administrative endpoints."""
    admin_client = get_role_client(dev_app, seeded_users['ADMIN'])
    admin_routes = [
        '/admin/users',
        '/admin/roles',
        '/admin/audit-logs',
        '/academic/campuses',
        '/finance/fee-types',
        '/reports/fees'
    ]
    for r in admin_routes:
        resp = admin_client.get(r)
        assert resp.status_code == 200, f"Admin was denied access to {r} ({resp.status_code})"

def test_teacher_rbac_boundaries(dev_app, seeded_users):
    """Teacher has access to academic/instructional areas, but 403 on admin-only areas."""
    teacher_client = get_role_client(dev_app, seeded_users['TEACHER'])
    
    # Allowed routes
    allowed = ['/dashboard', '/instructors', '/classes/sections', '/classes/attendance']
    for r in allowed:
        resp = teacher_client.get(r)
        assert resp.status_code == 200, f"Teacher should access {r}, got {resp.status_code}"

    # Prohibited admin routes (must return 403)
    forbidden = [
        '/admin/users',
        '/admin/roles',
        '/admin/audit-logs',
        '/reports/attendance',
        '/finance/fee-types/add',
        '/academic/campuses/add'
    ]
    for r in forbidden:
        resp = teacher_client.get(r)
        assert resp.status_code == 403, f"Teacher should be denied on {r}, got {resp.status_code}"

def test_student_rbac_boundaries(dev_app, seeded_users):
    """Student has access to student portal routes, but 403 on admin, instructor and management routes."""
    student_client = get_role_client(dev_app, seeded_users['STUDENT'])
    
    # Allowed routes
    allowed = ['/dashboard', '/classes/enrollments', '/finance/invoices']
    for r in allowed:
        resp = student_client.get(r)
        assert resp.status_code == 200, f"Student should access {r}, got {resp.status_code}"

    # Prohibited routes (must return 403)
    forbidden = [
        '/admin/users',
        '/admin/roles',
        '/instructors/add',
        '/classes/sections/add',
        '/academic/campuses/add',
        '/reports/fees'
    ]
    for r in forbidden:
        resp = student_client.get(r)
        assert resp.status_code == 403, f"Student should be denied on {r}, got {resp.status_code}"

def test_staff_rbac_boundaries(dev_app, seeded_users):
    """Staff has access to services and staff dashboard, but 403 on admin system routes."""
    staff_client = get_role_client(dev_app, seeded_users['STAFF'])
    
    # Allowed routes
    allowed = ['/dashboard', '/services/transport/routes', '/services/hostel/buildings']
    for r in allowed:
        resp = staff_client.get(r)
        assert resp.status_code == 200, f"Staff should access {r}, got {resp.status_code}"

    # Prohibited routes
    forbidden = [
        '/admin/users',
        '/admin/roles',
        '/admin/audit-logs'
    ]
    for r in forbidden:
        resp = staff_client.get(r)
        assert resp.status_code == 403, f"Staff should be denied on {r}, got {resp.status_code}"

def test_anonymous_redirects(dev_app):
    """Anonymous visitors must be redirected to /auth/login for protected pages."""
    anon_client = dev_app.test_client()
    resp = anon_client.get('/admin/users', follow_redirects=False)
    assert resp.status_code == 302
    assert '/auth/login' in resp.headers.get('Location', '')
