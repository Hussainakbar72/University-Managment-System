from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.extensions import db
from app.utils.decorators import admin_required
from app.models.auth import Instructor, User, Role, UserRole
from app.models.academic import Department
from app.forms.student_forms import InstructorForm

instructors_mgmt_bp = Blueprint('instructors_mgmt', __name__)

@instructors_mgmt_bp.route('/instructors')
@login_required
def list_instructors():
    search = request.args.get('search', '').strip()
    query = Instructor.query
    if search:
        query = query.filter(Instructor.employee_id.ilike(f'%{search}%') | Instructor.designation.ilike(f'%{search}%'))
    instructors = query.order_by(Instructor.id.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Faculty & Instructors', items=instructors,
                           columns=[('ID', 'id'), ('Emp #', 'employee_id'), ('Faculty Name', 'name'), ('Department', 'department_name'), ('Designation', 'designation'), ('Qualification', 'qualification')],
                           create_url=url_for('instructors_mgmt.create_instructor'), edit_endpoint='instructors_mgmt.edit_instructor', delete_endpoint='instructors_mgmt.delete_instructor')

@instructors_mgmt_bp.route('/instructors/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_instructor():
    form = InstructorForm()
    # Filter to only users with 'TEACHER' role who are not yet assigned to an instructor profile
    teacher_role = Role.query.filter(Role.name.ilike('TEACHER')).first()
    assigned_ids = [ins.user_id for ins in Instructor.query.all()]
    if teacher_role:
        available_users = User.query.join(UserRole).filter(
            UserRole.role_id == teacher_role.id,
            ~User.id.in_(assigned_ids)
        ).all()
    else:
        available_users = [u for u in User.query.all() if u.id not in assigned_ids and u.has_role('TEACHER')]

    form.user_id.choices = [(u.id, f"{u.full_name} ({u.email})") for u in available_users]
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    if form.validate_on_submit():
        if Instructor.query.filter_by(employee_id=form.employee_id.data.strip().upper()).first():
            flash('Employee ID already in use.', 'danger')
        else:
            ins = Instructor(
                user_id=form.user_id.data,
                employee_id=form.employee_id.data.strip().upper(),
                department_id=form.department_id.data,
                designation=form.designation.data,
                qualification=form.qualification.data,
                joining_date=form.joining_date.data
            )
            db.session.add(ins)
            db.session.commit()
            flash(f'Instructor "{ins.employee_id}" appointed successfully!', 'success')
            return redirect(url_for('instructors_mgmt.list_instructors'))
    return render_template('crud/form.html', title='Add Instructor', form=form, back_url=url_for('instructors_mgmt.list_instructors'))

@instructors_mgmt_bp.route('/instructors/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_instructor(id):
    ins = Instructor.query.get_or_404(id)
    form = InstructorForm(obj=ins)
    # Filter to only users with 'TEACHER' role (including the currently edited instructor's user account)
    teacher_role = Role.query.filter(Role.name.ilike('TEACHER')).first()
    other_assigned_ids = [i.user_id for i in Instructor.query.filter(Instructor.id != ins.id).all()]
    if teacher_role:
        available_users = User.query.join(UserRole).filter(
            UserRole.role_id == teacher_role.id,
            ~User.id.in_(other_assigned_ids)
        ).all()
    else:
        available_users = [u for u in User.query.all() if (u.id not in other_assigned_ids or u.id == ins.user_id) and u.has_role('TEACHER')]

    if ins.user and ins.user not in available_users:
        available_users.insert(0, ins.user)

    form.user_id.choices = [(u.id, f"{u.full_name} ({u.email})") for u in available_users]
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    if form.validate_on_submit():
        form.populate_obj(ins)
        ins.employee_id = form.employee_id.data.strip().upper()
        db.session.commit()
        flash(f'Instructor record updated!', 'success')
        return redirect(url_for('instructors_mgmt.list_instructors'))
    return render_template('crud/form.html', title='Edit Instructor', form=form, back_url=url_for('instructors_mgmt.list_instructors'))

@instructors_mgmt_bp.route('/instructors/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_instructor(id):
    ins = Instructor.query.get_or_404(id)
    emp = ins.employee_id
    db.session.delete(ins)
    db.session.commit()
    flash(f'Instructor "{emp}" deleted.', 'info')
    return redirect(url_for('instructors_mgmt.list_instructors'))
