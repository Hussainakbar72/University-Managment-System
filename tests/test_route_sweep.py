import pytest
from app import create_app
from app.models.auth import User

@pytest.fixture(scope='module')
def dev_app():
    """Create app bound to development/seeded database."""
    app = create_app('development')
    return app

def test_route_sweep_baseline(dev_app):
    """
    T1: Automated sweep asserting exact baseline numbers on the 106 parameterless GET routes:
    - Admin: 103 x 200, 3 x 302, 0 x 403, 0 x 500
    - Teacher: 49 x 200, 54 x 403, 3 x 302, 0 x 500
    - Student: 45 x 200, 58 x 403, 3 x 302, 0 x 500
    - Staff: 45 x 200, 58 x 403, 3 x 302, 0 x 500
    - Anonymous: 1 x 200, 105 x 302, 0 x 403, 0 x 500
    - Zero 500 errors across all roles
    """
    routes = []
    for rule in dev_app.url_map.iter_rules():
        if 'GET' in rule.methods and '<' not in rule.rule and not rule.rule.startswith('/static'):
            routes.append(rule.rule)
    routes = sorted(list(set(routes)))
    assert len(routes) == 106, f"Expected 106 parameterless GET routes, found {len(routes)}"

    roles = [
        ('admin', 'admin@ums.edu'),
        ('teacher', 'dr.tariq@ums.edu'),
        ('student', 'ali.raza@ums.edu'),
        ('staff', 'staff.kamran@ums.edu'),
        ('anonymous', None)
    ]

    user_ids = {}
    with dev_app.app_context():
        for role_name, email in roles:
            if email:
                u = User.query.filter_by(email=email).first()
                assert u is not None, f"Seeded user {email} not found"
                user_ids[role_name] = str(u.id)

    results = {}
    for role_name, email in roles:
        results[role_name] = {}
        counts = {}
        uid = user_ids.get(role_name)

        for r in routes:
            client = dev_app.test_client()
            if uid:
                with client.session_transaction() as sess:
                    sess['_user_id'] = uid
                    sess['_fresh'] = True
            res = client.get(r, follow_redirects=False)
            counts[res.status_code] = counts.get(res.status_code, 0) + 1
            results[role_name][r] = res.status_code

        # Zero 500s across all roles
        assert counts.get(500, 0) == 0, f"Role {role_name} encountered 500 error on one or more routes!"

    # Admin assertions: 103 x 200, 3 x 302 (auth.login, auth.profile redirect or similar)
    assert counts_by_status(results['admin'], 200) == 103
    assert counts_by_status(results['admin'], 302) == 3
    assert counts_by_status(results['admin'], 403) == 0

    # Teacher assertions: 49 x 200, 54 x 403, 3 x 302
    assert counts_by_status(results['teacher'], 200) == 49
    assert counts_by_status(results['teacher'], 403) == 54
    assert counts_by_status(results['teacher'], 302) == 3

    # Student assertions: 45 x 200, 58 x 403, 3 x 302
    assert counts_by_status(results['student'], 200) == 45
    assert counts_by_status(results['student'], 403) == 58
    assert counts_by_status(results['student'], 302) == 3

    # Staff assertions: 45 x 200, 58 x 403, 3 x 302
    assert counts_by_status(results['staff'], 200) == 45
    assert counts_by_status(results['staff'], 403) == 58
    assert counts_by_status(results['staff'], 302) == 3

    # Anonymous assertions: 1 x 200 (/auth/login), 105 x 302
    assert counts_by_status(results['anonymous'], 200) == 1
    assert counts_by_status(results['anonymous'], 302) == 105
    assert counts_by_status(results['anonymous'], 403) == 0

def counts_by_status(status_map, status_code):
    return sum(1 for code in status_map.values() if code == status_code)
