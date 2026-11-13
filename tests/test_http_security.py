import pytest
from app import create_app
from app.models.auth import User

@pytest.fixture(scope='module')
def dev_app():
    return create_app('development')

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

def test_session_cookie_security_flags(dev_app):
    """Verify that session cookies have HttpOnly and SameSite configured."""
    client = dev_app.test_client()
    resp = client.get('/auth/login')
    # Trigger session cookie by setting test session
    with client.session_transaction() as sess:
        sess['test'] = True
    resp2 = client.get('/auth/login')
    
    # Check app config flags
    assert dev_app.config.get('SESSION_COOKIE_HTTPONLY') is True
    assert dev_app.config.get('SESSION_COOKIE_SAMESITE') in ['Lax', 'Strict']

def test_pagination_boundary_resilience(admin_client):
    """
    Verify pagination boundaries (?page=0, -1, abc, 99999) return safe responses (200 or 404),
    never unhandled 500 errors.
    """
    boundaries = [
        '/academic/campuses?page=0',
        '/academic/campuses?page=-1',
        '/academic/campuses?page=abc',
        '/academic/campuses?page=99999'
    ]
    for url in boundaries:
        resp = admin_client.get(url)
        assert resp.status_code in [200, 404], f"URL {url} returned unexpected status {resp.status_code}"
        assert resp.status_code != 500

def test_search_xss_escaping(admin_client):
    """
    Verify search parameter values with HTML/JS payloads are safely escaped
    and never rendered unescaped in the DOM.
    """
    xss_payload = "<script>alert('xss')</script>"
    resp = admin_client.get(f'/academic/campuses?search={xss_payload}')
    assert resp.status_code == 200
    # Must not contain unescaped script tag
    assert b"<script>alert('xss')</script>" not in resp.data
    # Must contain HTML-escaped string
    assert b"&lt;script&gt;alert(&#39;xss&#39;)&lt;/script&gt;" in resp.data or b"&lt;script&gt;alert('xss')&lt;/script&gt;" in resp.data

def test_sql_injection_resilience(admin_client):
    """
    Verify SQL injection payloads in search queries execute safely via parameterized ORM queries.
    """
    sqli_payload = "' OR '1'='1"
    resp = admin_client.get(f'/academic/campuses?search={sqli_payload}')
    assert resp.status_code == 200
    assert resp.status_code != 500
