from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.extensions import db
from app.utils.decorators import admin_required
from app.models.auth import Student, Guardian, StudentGuardian, User, Role, UserRole
from app.models.academic import Program
from app.forms.student_forms import StudentForm, GuardianForm, StudentGuardianForm

students_mgmt_bp = Blueprint('students_mgmt', __name__)

# ----------------- 1. STUDENTS -----------------
@students_mgmt_bp.route('/students')
@login_required
def list_students():
    search = request.args.get('search', '').strip()
    query = Student.query
    if search:
        query = query.filter(Student.registration_number.ilike(f'%{search}%'))
    students = query.order_by(Student.id.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Students Directory', items=students,
                           columns=[('ID', 'id'), ('Reg #', 'registration_number'), ('Student Name', 'student_name'), ('Program', 'program_code'), ('Semester', 'current_semester'), ('Status', 'status'), ('CGPA', 'cgpa')],
                           create_url=url_for('students_mgmt.create_student'), edit_endpoint='students_mgmt.edit_student', delete_endpoint='students_mgmt.delete_student')

@students_mgmt_bp.route('/students/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_student():
    form = StudentForm()
    # Filter to only users with 'STUDENT' role who are not yet linked to an existing student record
    student_role = Role.query.filter(Role.name.ilike('STUDENT')).first()
    assigned_ids = [s.user_id for s in Student.query.all()]
    if student_role:
        available_users = User.query.join(UserRole).filter(
            UserRole.role_id == student_role.id,
            ~User.id.in_(assigned_ids)
        ).all()
    else:
        available_users = [u for u in User.query.all() if u.id not in assigned_ids and u.has_role('STUDENT')]

    form.user_id.choices = [(u.id, f"{u.full_name} ({u.email})") for u in available_users]
    form.program_id.choices = [(p.id, f"{p.code} - {p.name}") for p in Program.query.all()]
    if form.validate_on_submit():
        if Student.query.filter_by(registration_number=form.registration_number.data.strip().upper()).first():
            flash('Registration number is already in use.', 'danger')
        else:
            student = Student(
                user_id=form.user_id.data,
                registration_number=form.registration_number.data.strip().upper(),
                program_id=form.program_id.data,
                admission_date=form.admission_date.data,
                current_semester=form.current_semester.data,
                status=form.status.data,
                cgpa=form.cgpa.data or 0.00
            )
            db.session.add(student)
            db.session.commit()
            flash(f'Student "{student.registration_number}" registered successfully!', 'success')
            return redirect(url_for('students_mgmt.list_students'))
    return render_template('crud/form.html', title='Register Student', form=form, back_url=url_for('students_mgmt.list_students'))

@students_mgmt_bp.route('/students/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_student(id):
    student = Student.query.get_or_404(id)
    form = StudentForm(obj=student)
    # Filter to only users with 'STUDENT' role (including the currently edited student's user account)
    student_role = Role.query.filter(Role.name.ilike('STUDENT')).first()
    other_assigned_ids = [s.user_id for s in Student.query.filter(Student.id != student.id).all()]
    if student_role:
        available_users = User.query.join(UserRole).filter(
            UserRole.role_id == student_role.id,
            ~User.id.in_(other_assigned_ids)
        ).all()
    else:
        available_users = [u for u in User.query.all() if (u.id not in other_assigned_ids or u.id == student.user_id) and u.has_role('STUDENT')]

    if student.user and student.user not in available_users:
        available_users.insert(0, student.user)

    form.user_id.choices = [(u.id, f"{u.full_name} ({u.email})") for u in available_users]
    form.program_id.choices = [(p.id, f"{p.code} - {p.name}") for p in Program.query.all()]
    if form.validate_on_submit():
        form.populate_obj(student)
        student.registration_number = form.registration_number.data.strip().upper()
        db.session.commit()
        flash(f'Student "{student.registration_number}" updated!', 'success')
        return redirect(url_for('students_mgmt.list_students'))
    return render_template('crud/form.html', title='Edit Student', form=form, back_url=url_for('students_mgmt.list_students'))

@students_mgmt_bp.route('/students/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    reg = student.registration_number
    db.session.delete(student)
    db.session.commit()
    flash(f'Student "{reg}" deleted.', 'info')
    return redirect(url_for('students_mgmt.list_students'))


# ----------------- 2. GUARDIANS -----------------
@students_mgmt_bp.route('/guardians')
@login_required
def list_guardians():
    guardians = Guardian.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Student Guardians', items=guardians,
                           columns=[('ID', 'id'), ('Full Name', 'full_name'), ('Relationship', 'relationship'), ('Phone', 'phone'), ('Email', 'email')],
                           create_url=url_for('students_mgmt.create_guardian'), edit_endpoint='students_mgmt.edit_guardian', delete_endpoint='students_mgmt.delete_guardian')

@students_mgmt_bp.route('/guardians/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_guardian():
    form = GuardianForm()
    if form.validate_on_submit():
        guardian = Guardian(full_name=form.full_name.data, relationship=form.relationship.data, phone=form.phone.data, email=form.email.data, occupation=form.occupation.data, address=form.address.data)
        db.session.add(guardian)
        db.session.commit()
        flash(f'Guardian "{guardian.full_name}" added!', 'success')
        return redirect(url_for('students_mgmt.list_guardians'))
    return render_template('crud/form.html', title='Add Guardian', form=form, back_url=url_for('students_mgmt.list_guardians'))

@students_mgmt_bp.route('/guardians/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_guardian(id):
    guardian = Guardian.query.get_or_404(id)
    form = GuardianForm(obj=guardian)
    if form.validate_on_submit():
        form.populate_obj(guardian)
        db.session.commit()
        flash('Guardian details updated!', 'success')
        return redirect(url_for('students_mgmt.list_guardians'))
    return render_template('crud/form.html', title='Edit Guardian', form=form, back_url=url_for('students_mgmt.list_guardians'))

@students_mgmt_bp.route('/guardians/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_guardian(id):
    guardian = Guardian.query.get_or_404(id)
    db.session.delete(guardian)
    db.session.commit()
    flash('Guardian record deleted.', 'info')
    return redirect(url_for('students_mgmt.list_guardians'))


# ----------------- 3. STUDENT GUARDIANS (JUNCTION) -----------------
@students_mgmt_bp.route('/student-guardians')
@login_required
def list_student_guardians():
    links = StudentGuardian.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Student Guardian Links', items=links,
                           columns=[('ID', 'id'), ('Student ID', 'student_id'), ('Guardian ID', 'guardian_id'), ('Primary Contact', 'is_primary')],
                           create_url=url_for('students_mgmt.create_student_guardian'), edit_endpoint='students_mgmt.edit_student_guardian', delete_endpoint='students_mgmt.delete_student_guardian')

@students_mgmt_bp.route('/student-guardians/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_student_guardian():
    form = StudentGuardianForm()
    form.student_id.choices = [(s.id, f"{s.registration_number}") for s in Student.query.all()]
    form.guardian_id.choices = [(g.id, f"{g.full_name} ({g.relationship})") for g in Guardian.query.all()]
    if form.validate_on_submit():
        link = StudentGuardian(student_id=form.student_id.data, guardian_id=form.guardian_id.data, is_primary=form.is_primary.data)
        db.session.add(link)
        db.session.commit()
        flash('Guardian linked to student successfully!', 'success')
        return redirect(url_for('students_mgmt.list_student_guardians'))
    return render_template('crud/form.html', title='Link Guardian to Student', form=form, back_url=url_for('students_mgmt.list_student_guardians'))

@students_mgmt_bp.route('/student-guardians/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_student_guardian(id):
    link = StudentGuardian.query.get_or_404(id)
    form = StudentGuardianForm(obj=link)
    form.student_id.choices = [(s.id, f"{s.registration_number}") for s in Student.query.all()]
    form.guardian_id.choices = [(g.id, f"{g.full_name} ({g.relationship})") for g in Guardian.query.all()]
    if form.validate_on_submit():
        form.populate_obj(link)
        db.session.commit()
        flash('Link updated!', 'success')
        return redirect(url_for('students_mgmt.list_student_guardians'))
    return render_template('crud/form.html', title='Edit Guardian Link', form=form, back_url=url_for('students_mgmt.list_student_guardians'))

@students_mgmt_bp.route('/student-guardians/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_student_guardian(id):
    link = StudentGuardian.query.get_or_404(id)
    db.session.delete(link)
    db.session.commit()
    flash('Guardian link removed.', 'info')
    return redirect(url_for('students_mgmt.list_student_guardians'))
