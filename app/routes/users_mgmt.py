from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.utils.decorators import admin_required
from app.models.auth import User, Role, UserRole, Staff
from app.models.academic import Department
from app.models.system import AuditLog
from app.forms.auth_forms import UserForm, RoleForm, UserRoleForm
from app.forms.student_forms import StaffForm
from app.forms.service_forms import AuditLogForm

users_mgmt_bp = Blueprint('users_mgmt', __name__, url_prefix='/admin')

# ----------------- 1. USERS -----------------
@users_mgmt_bp.route('/users')
@login_required
@admin_required
def list_users():
    search = request.args.get('search', '').strip()
    query = User.query
    if search:
        query = query.filter(User.email.ilike(f'%{search}%') | User.first_name.ilike(f'%{search}%') | User.last_name.ilike(f'%{search}%'))
    users = query.order_by(User.id.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='User Accounts', items=users,
                           columns=[('ID', 'id'), ('Email', 'email'), ('Name', 'full_name'), ('Phone', 'phone'), ('Active', 'is_active')],
                           create_url=url_for('users_mgmt.create_user'), edit_endpoint='users_mgmt.edit_user', delete_endpoint='users_mgmt.delete_user')

@users_mgmt_bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    form = UserForm()
    roles = Role.query.all()
    form.role_id.choices = [(r.id, r.name) for r in roles]
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data.strip().lower()).first():
            flash('Email address is already registered.', 'danger')
        else:
            user = User(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data.strip().lower(),
                phone=form.phone.data,
                is_active=form.is_active.data
            )
            user.set_password(form.password.data or 'Password@123')
            db.session.add(user)
            db.session.flush()

            # Assign selected role
            ur = UserRole(user_id=user.id, role_id=form.role_id.data)
            db.session.add(ur)

            log = AuditLog(user_id=current_user.id, action='CREATE_USER', table_name='users', record_id=user.id, details=f"Created user {user.email}")
            db.session.add(log)
            db.session.commit()

            flash(f'User "{user.full_name}" registered successfully!', 'success')
            return redirect(url_for('users_mgmt.list_users'))
    return render_template('crud/form.html', title='Create User', form=form, back_url=url_for('users_mgmt.list_users'))

@users_mgmt_bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(id):
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    roles = Role.query.all()
    form.role_id.choices = [(r.id, r.name) for r in roles]
    if request.method == 'GET' and user.roles:
        form.role_id.data = user.roles[0].role_id

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data.strip().lower()
        user.phone = form.phone.data
        user.is_active = form.is_active.data
        if form.password.data:
            user.set_password(form.password.data)
        
        # Update primary role
        if user.roles:
            user.roles[0].role_id = form.role_id.data
        else:
            db.session.add(UserRole(user_id=user.id, role_id=form.role_id.data))

        db.session.commit()
        flash(f'User "{user.full_name}" updated!', 'success')
        return redirect(url_for('users_mgmt.list_users'))
    return render_template('crud/form.html', title='Edit User', form=form, back_url=url_for('users_mgmt.list_users'))

@users_mgmt_bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(id):
    if id == current_user.id:
        flash('You cannot delete your own account.', 'danger')
        return redirect(url_for('users_mgmt.list_users'))
    user = User.query.get_or_404(id)
    name = user.full_name
    db.session.delete(user)
    db.session.commit()
    flash(f'User "{name}" deleted.', 'info')
    return redirect(url_for('users_mgmt.list_users'))


# ----------------- 2. ROLES -----------------
@users_mgmt_bp.route('/roles')
@login_required
@admin_required
def list_roles():
    roles = Role.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Security Roles', items=roles,
                           columns=[('ID', 'id'), ('Name', 'name'), ('Description', 'description')],
                           create_url=url_for('users_mgmt.create_role'), edit_endpoint='users_mgmt.edit_role', delete_endpoint='users_mgmt.delete_role')

@users_mgmt_bp.route('/roles/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_role():
    form = RoleForm()
    if form.validate_on_submit():
        role = Role(name=form.name.data.upper(), description=form.description.data)
        db.session.add(role)
        db.session.commit()
        flash(f'Role "{role.name}" created!', 'success')
        return redirect(url_for('users_mgmt.list_roles'))
    return render_template('crud/form.html', title='Add Role', form=form, back_url=url_for('users_mgmt.list_roles'))

@users_mgmt_bp.route('/roles/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_role(id):
    role = Role.query.get_or_404(id)
    form = RoleForm(obj=role)
    if form.validate_on_submit():
        form.populate_obj(role)
        role.name = form.name.data.upper()
        db.session.commit()
        flash(f'Role updated!', 'success')
        return redirect(url_for('users_mgmt.list_roles'))
    return render_template('crud/form.html', title='Edit Role', form=form, back_url=url_for('users_mgmt.list_roles'))

@users_mgmt_bp.route('/roles/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_role(id):
    role = Role.query.get_or_404(id)
    db.session.delete(role)
    db.session.commit()
    flash('Role deleted.', 'info')
    return redirect(url_for('users_mgmt.list_roles'))


# ----------------- 3. USER ROLES -----------------
@users_mgmt_bp.route('/user-roles')
@login_required
@admin_required
def list_user_roles():
    urs = UserRole.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Role Assignments', items=urs,
                           columns=[('ID', 'id'), ('User ID', 'user_id'), ('Role ID', 'role_id'), ('Assigned Date', 'assigned_at')],
                           create_url=url_for('users_mgmt.create_user_role'), edit_endpoint='users_mgmt.edit_user_role', delete_endpoint='users_mgmt.delete_user_role')

@users_mgmt_bp.route('/user-roles/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user_role():
    form = UserRoleForm()
    form.user_id.choices = [(u.id, f"{u.full_name} ({u.email})") for u in User.query.all()]
    form.role_id.choices = [(r.id, r.name) for r in Role.query.all()]
    if form.validate_on_submit():
        existing = UserRole.query.filter_by(user_id=form.user_id.data, role_id=form.role_id.data).first()
        if existing:
            flash('This role is already assigned to the user.', 'warning')
        else:
            ur = UserRole(user_id=form.user_id.data, role_id=form.role_id.data)
            db.session.add(ur)
            db.session.commit()
            flash('Role assigned successfully!', 'success')
            return redirect(url_for('users_mgmt.list_user_roles'))
    return render_template('crud/form.html', title='Assign User Role', form=form, back_url=url_for('users_mgmt.list_user_roles'))

@users_mgmt_bp.route('/user-roles/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user_role(id):
    ur = UserRole.query.get_or_404(id)
    form = UserRoleForm(obj=ur)
    form.user_id.choices = [(u.id, f"{u.full_name} ({u.email})") for u in User.query.all()]
    form.role_id.choices = [(r.id, r.name) for r in Role.query.all()]
    if form.validate_on_submit():
        form.populate_obj(ur)
        db.session.commit()
        flash('Assignment updated!', 'success')
        return redirect(url_for('users_mgmt.list_user_roles'))
    return render_template('crud/form.html', title='Edit User Role', form=form, back_url=url_for('users_mgmt.list_user_roles'))

@users_mgmt_bp.route('/user-roles/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user_role(id):
    ur = UserRole.query.get_or_404(id)
    db.session.delete(ur)
    db.session.commit()
    flash('Role assignment removed.', 'info')
    return redirect(url_for('users_mgmt.list_user_roles'))


# ----------------- 4. STAFF -----------------
@users_mgmt_bp.route('/staff')
@login_required
@admin_required
def list_staff():
    staff_members = Staff.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Administrative Staff', items=staff_members,
                           columns=[('ID', 'id'), ('Employee ID', 'employee_id'), ('Job Title', 'job_title'), ('Department ID', 'department_id'), ('Hire Date', 'hire_date')],
                           create_url=url_for('users_mgmt.create_staff'), edit_endpoint='users_mgmt.edit_staff', delete_endpoint='users_mgmt.delete_staff')

@users_mgmt_bp.route('/staff/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_staff():
    form = StaffForm()
    form.user_id.choices = [(u.id, f"{u.full_name} ({u.email})") for u in User.query.all()]
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    if form.validate_on_submit():
        staff = Staff(user_id=form.user_id.data, employee_id=form.employee_id.data, department_id=form.department_id.data, job_title=form.job_title.data, hire_date=form.hire_date.data)
        db.session.add(staff)
        db.session.commit()
        flash(f'Staff member "{staff.employee_id}" created!', 'success')
        return redirect(url_for('users_mgmt.list_staff'))
    return render_template('crud/form.html', title='Add Staff Member', form=form, back_url=url_for('users_mgmt.list_staff'))

@users_mgmt_bp.route('/staff/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_staff(id):
    staff = Staff.query.get_or_404(id)
    form = StaffForm(obj=staff)
    form.user_id.choices = [(u.id, f"{u.full_name} ({u.email})") for u in User.query.all()]
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    if form.validate_on_submit():
        form.populate_obj(staff)
        db.session.commit()
        flash('Staff record updated!', 'success')
        return redirect(url_for('users_mgmt.list_staff'))
    return render_template('crud/form.html', title='Edit Staff', form=form, back_url=url_for('users_mgmt.list_staff'))

@users_mgmt_bp.route('/staff/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_staff(id):
    staff = Staff.query.get_or_404(id)
    db.session.delete(staff)
    db.session.commit()
    flash('Staff record deleted.', 'info')
    return redirect(url_for('users_mgmt.list_staff'))


# ----------------- 5. AUDIT LOGS -----------------
@users_mgmt_bp.route('/audit-logs')
@login_required
@admin_required
def list_audit_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=15)
    return render_template('crud/list.html', title='System Audit Logs', items=logs,
                           columns=[('ID', 'id'), ('Action', 'action'), ('Table', 'table_name'), ('Record ID', 'record_id'), ('Timestamp', 'timestamp')],
                           create_url=url_for('users_mgmt.create_audit_log'), edit_endpoint='users_mgmt.edit_audit_log', delete_endpoint='users_mgmt.delete_audit_log')

@users_mgmt_bp.route('/audit-logs/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_audit_log():
    form = AuditLogForm()
    users = [(0, '-- System / Anonymous --')] + [(u.id, u.email) for u in User.query.all()]
    form.user_id.choices = users
    if form.validate_on_submit():
        user_id = form.user_id.data if form.user_id.data != 0 else None
        log = AuditLog(user_id=user_id, action=form.action.data, table_name=form.table_name.data, record_id=form.record_id.data, ip_address=form.ip_address.data or request.remote_addr, details=form.details.data)
        db.session.add(log)
        db.session.commit()
        flash('Audit log entry created!', 'success')
        return redirect(url_for('users_mgmt.list_audit_logs'))
    return render_template('crud/form.html', title='Add Audit Log', form=form, back_url=url_for('users_mgmt.list_audit_logs'))

@users_mgmt_bp.route('/audit-logs/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_audit_log(id):
    log = AuditLog.query.get_or_404(id)
    form = AuditLogForm(obj=log)
    users = [(0, '-- System / Anonymous --')] + [(u.id, u.email) for u in User.query.all()]
    form.user_id.choices = users
    if form.validate_on_submit():
        form.populate_obj(log)
        log.user_id = form.user_id.data if form.user_id.data != 0 else None
        db.session.commit()
        flash('Audit log entry updated!', 'success')
        return redirect(url_for('users_mgmt.list_audit_logs'))
    return render_template('crud/form.html', title='Edit Audit Log', form=form, back_url=url_for('users_mgmt.list_audit_logs'))

@users_mgmt_bp.route('/audit-logs/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_audit_log(id):
    log = AuditLog.query.get_or_404(id)
    db.session.delete(log)
    db.session.commit()
    flash('Audit log entry deleted.', 'info')
    return redirect(url_for('users_mgmt.list_audit_logs'))
