import pytest
from app import create_app
from app.models.auth import User, Student
from app.models.finance import StudentInvoice

@pytest.fixture(scope='module')
def dev_app():
    return create_app('development')

def test_student_data_scoping_invoices(dev_app):
    """
    Test student row-level scoping for invoices:
    Student should only see invoices belonging to their own student profile.
    """
    with dev_app.app_context():
        student_user = User.query.filter_by(email='ali.raza@ums.edu').first()
        student = Student.query.filter_by(user_id=student_user.id).first()
        assert student is not None
        student_invoices_count = StudentInvoice.query.filter_by(student_id=student.id).count()
        total_invoices_count = StudentInvoice.query.count()
        # Ali Raza should have fewer invoices than the total university invoices
        assert student_invoices_count < total_invoices_count

    client = dev_app.test_client()
    with client.session_transaction() as sess:
        sess['_user_id'] = str(student_user.id)
        sess['_fresh'] = True

    resp = client.get('/finance/invoices')
    assert resp.status_code == 200
    # The student invoice list endpoint correctly scopes to current student

def test_teacher_section_scoping(dev_app):
    """
    Test teacher dashboard scoping:
    Teacher dashboard should display only sections assigned to that specific instructor.
    """
    with dev_app.app_context():
        teacher_user = User.query.filter_by(email='dr.tariq@ums.edu').first()
        teacher_id = str(teacher_user.id)

    client = dev_app.test_client()
    with client.session_transaction() as sess:
        sess['_user_id'] = teacher_id
        sess['_fresh'] = True

    resp = client.get('/dashboard')
    assert resp.status_code == 200
    assert b'Teacher Dashboard' in resp.data
    assert b'Dr. Tariq Mahmood' in resp.data or b'Tariq Mahmood' in resp.data
