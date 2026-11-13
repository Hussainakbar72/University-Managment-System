import pytest
from app import create_app
from app.extensions import db
from app.models.auth import User
from app.models.academic import Campus

@pytest.fixture(scope='module')
def dev_app():
    app = create_app('development')
    app.config['WTF_CSRF_ENABLED'] = False
    return app

@pytest.fixture(scope='module')
def admin_client(dev_app):
    with dev_app.app_context():
        admin = User.query.filter_by(email='admin@ums.edu').first()
        admin_id = str(admin.id)
    client = dev_app.test_client()
    with client.session_transaction() as sess:
        sess['_user_id'] = admin_id
        sess['_fresh'] = True
    return client

def test_crud_http_lifecycle(dev_app, admin_client):
    """
    T3: End-to-end HTTP CRUD Lifecycle test.
    - GET list page
    - GET add form
    - POST add form (validation error handling)
    - POST add form (successful creation)
    - GET edit form
    - POST edit form (successful update)
    - POST delete (cleanup)
    """
    # 1. GET list
    resp = admin_client.get('/academic/campuses')
    assert resp.status_code == 200
    assert b'Campuses' in resp.data

    # 2. GET add form
    resp = admin_client.get('/academic/campuses/add')
    assert resp.status_code == 200
    assert b'Add Campus' in resp.data
    assert b'<form' in resp.data

    # 3. POST add with invalid data (empty name)
    resp = admin_client.post('/academic/campuses/add', data={
        'name': '',
        'code': 'TST-99',
        'address': 'Test Street',
        'city': 'Lahore',
        'is_main': 'y'
    })
    # Form redisplays with validation error
    assert resp.status_code == 200

    # 4. POST add with valid data
    resp = admin_client.post('/academic/campuses/add', data={
        'name': 'Test Http Campus',
        'code': 'THC-01',
        'address': '42 Cyber Way',
        'city': 'Islamabad',
        'is_main': False
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'created successfully' in resp.data

    # Retrieve created ID
    with dev_app.app_context():
        created = Campus.query.filter_by(code='THC-01').first()
        assert created is not None
        campus_id = created.id
        assert created.city == 'Islamabad'

    # 5. GET edit form
    resp = admin_client.get(f'/academic/campuses/{campus_id}/edit')
    assert resp.status_code == 200
    assert b'Edit Campus' in resp.data
    assert b'THC-01' in resp.data

    # 6. POST edit form
    resp = admin_client.post(f'/academic/campuses/{campus_id}/edit', data={
        'name': 'Updated Http Campus',
        'code': 'THC-02',
        'address': '99 New Ave',
        'city': 'Rawalpindi',
        'is_main': True
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b'updated successfully' in resp.data

    with dev_app.app_context():
        updated = Campus.query.get(campus_id)
        assert updated.name == 'Updated Http Campus'
        assert updated.code == 'THC-02'

    # 7. POST delete
    resp = admin_client.post(f'/academic/campuses/{campus_id}/delete', follow_redirects=True)
    assert resp.status_code == 200
    assert b'deleted successfully' in resp.data

    with dev_app.app_context():
        deleted = Campus.query.filter_by(code='THC-02').first()
        assert deleted is None

def test_fk_integrity_delete_protection(dev_app, admin_client):
    """
    Empirical verification for Backend Finding (documented in docs/BUGS.md):
    Deleting an entity that has active foreign key dependencies triggers an IntegrityError
    because CRUD delete handlers lack try/except IntegrityError rollback guards.
    """
    with dev_app.app_context():
        main_campus = Campus.query.filter_by(is_main=True).first()
        assert main_campus is not None
        main_id = main_campus.id

    with pytest.raises(Exception) as exc_info:
        admin_client.post(f'/academic/campuses/{main_id}/delete', follow_redirects=True)
    assert 'IntegrityError' in type(exc_info.value).__name__

def test_csrf_protection_enforcement():
    """Verify that CSRF is strictly enforced when CSRF is enabled."""
    csrf_app = create_app('testing')
    csrf_app.config['WTF_CSRF_ENABLED'] = True

    client = csrf_app.test_client()
    # Unauthenticated / un-tokenized POST should be rejected with 400
    resp = client.post('/auth/login', data={'email': 'admin@ums.edu', 'password': 'Password'})
    assert resp.status_code == 400
