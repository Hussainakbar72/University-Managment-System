from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from app.extensions import db
from app.utils.decorators import admin_required
from app.models.academic import (
    Campus, Faculty, Department, Program, AcademicYear, Semester, Course, CoursePrerequisite
)
from app.forms.academic_forms import (
    CampusForm, FacultyForm, DepartmentForm, ProgramForm,
    AcademicYearForm, SemesterForm, CourseForm, CoursePrerequisiteForm
)

academic_bp = Blueprint('academic', __name__, url_prefix='/academic')

# ----------------- 1. CAMPUSES -----------------
@academic_bp.route('/campuses')
@login_required
def list_campuses():
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    query = Campus.query
    if search:
        query = query.filter(Campus.name.ilike(f'%{search}%') | Campus.city.ilike(f'%{search}%'))
    campuses = query.paginate(page=page, per_page=10)
    return render_template('crud/list.html', title='Campuses', items=campuses,
                           columns=[('ID', 'id'), ('Name', 'name'), ('Code', 'code'), ('City', 'city'), ('Is Main', 'is_main')],
                           create_url=url_for('academic.create_campus'), edit_endpoint='academic.edit_campus', delete_endpoint='academic.delete_campus')

@academic_bp.route('/campuses/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_campus():
    form = CampusForm()
    if form.validate_on_submit():
        campus = Campus(name=form.name.data, code=form.code.data.upper(), address=form.address.data, city=form.city.data, is_main=form.is_main.data)
        db.session.add(campus)
        db.session.commit()
        flash(f'Campus "{campus.name}" created successfully!', 'success')
        return redirect(url_for('academic.list_campuses'))
    return render_template('crud/form.html', title='Add Campus', form=form, back_url=url_for('academic.list_campuses'))

@academic_bp.route('/campuses/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_campus(id):
    campus = Campus.query.get_or_404(id)
    form = CampusForm(obj=campus)
    if form.validate_on_submit():
        form.populate_obj(campus)
        campus.code = form.code.data.upper()
        db.session.commit()
        flash(f'Campus "{campus.name}" updated successfully!', 'success')
        return redirect(url_for('academic.list_campuses'))
    return render_template('crud/form.html', title='Edit Campus', form=form, back_url=url_for('academic.list_campuses'))

@academic_bp.route('/campuses/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_campus(id):
    campus = Campus.query.get_or_404(id)
    name = campus.name
    db.session.delete(campus)
    db.session.commit()
    flash(f'Campus "{name}" deleted successfully.', 'info')
    return redirect(url_for('academic.list_campuses'))


# ----------------- 2. FACULTIES -----------------
@academic_bp.route('/faculties')
@login_required
def list_faculties():
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    query = Faculty.query
    if search:
        query = query.filter(Faculty.name.ilike(f'%{search}%'))
    faculties = query.paginate(page=page, per_page=10)
    return render_template('crud/list.html', title='Faculties', items=faculties,
                           columns=[('ID', 'id'), ('Name', 'name'), ('Code', 'code'), ('Dean', 'dean_name')],
                           create_url=url_for('academic.create_faculty'), edit_endpoint='academic.edit_faculty', delete_endpoint='academic.delete_faculty')

@academic_bp.route('/faculties/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_faculty():
    form = FacultyForm()
    form.campus_id.choices = [(c.id, c.name) for c in Campus.query.all()]
    if form.validate_on_submit():
        faculty = Faculty(name=form.name.data, code=form.code.data.upper(), campus_id=form.campus_id.data, dean_name=form.dean_name.data)
        db.session.add(faculty)
        db.session.commit()
        flash(f'Faculty "{faculty.name}" created successfully!', 'success')
        return redirect(url_for('academic.list_faculties'))
    return render_template('crud/form.html', title='Add Faculty', form=form, back_url=url_for('academic.list_faculties'))

@academic_bp.route('/faculties/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_faculty(id):
    faculty = Faculty.query.get_or_404(id)
    form = FacultyForm(obj=faculty)
    form.campus_id.choices = [(c.id, c.name) for c in Campus.query.all()]
    if form.validate_on_submit():
        form.populate_obj(faculty)
        faculty.code = form.code.data.upper()
        db.session.commit()
        flash(f'Faculty "{faculty.name}" updated successfully!', 'success')
        return redirect(url_for('academic.list_faculties'))
    return render_template('crud/form.html', title='Edit Faculty', form=form, back_url=url_for('academic.list_faculties'))

@academic_bp.route('/faculties/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_faculty(id):
    faculty = Faculty.query.get_or_404(id)
    db.session.delete(faculty)
    db.session.commit()
    flash(f'Faculty deleted.', 'info')
    return redirect(url_for('academic.list_faculties'))


# ----------------- 3. DEPARTMENTS -----------------
@academic_bp.route('/departments')
@login_required
def list_departments():
    search = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    query = Department.query
    if search:
        query = query.filter(Department.name.ilike(f'%{search}%'))
    departments = query.paginate(page=page, per_page=10)
    return render_template('crud/list.html', title='Departments', items=departments,
                           columns=[('ID', 'id'), ('Name', 'name'), ('Code', 'code'), ('HOD', 'head_of_department')],
                           create_url=url_for('academic.create_department'), edit_endpoint='academic.edit_department', delete_endpoint='academic.delete_department')

@academic_bp.route('/departments/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_department():
    form = DepartmentForm()
    form.faculty_id.choices = [(f.id, f.name) for f in Faculty.query.all()]
    if form.validate_on_submit():
        dept = Department(name=form.name.data, code=form.code.data.upper(), faculty_id=form.faculty_id.data, head_of_department=form.head_of_department.data)
        db.session.add(dept)
        db.session.commit()
        flash(f'Department "{dept.name}" created successfully!', 'success')
        return redirect(url_for('academic.list_departments'))
    return render_template('crud/form.html', title='Add Department', form=form, back_url=url_for('academic.list_departments'))

@academic_bp.route('/departments/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_department(id):
    dept = Department.query.get_or_404(id)
    form = DepartmentForm(obj=dept)
    form.faculty_id.choices = [(f.id, f.name) for f in Faculty.query.all()]
    if form.validate_on_submit():
        form.populate_obj(dept)
        dept.code = form.code.data.upper()
        db.session.commit()
        flash(f'Department "{dept.name}" updated successfully!', 'success')
        return redirect(url_for('academic.list_departments'))
    return render_template('crud/form.html', title='Edit Department', form=form, back_url=url_for('academic.list_departments'))

@academic_bp.route('/departments/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_department(id):
    dept = Department.query.get_or_404(id)
    db.session.delete(dept)
    db.session.commit()
    flash('Department deleted.', 'info')
    return redirect(url_for('academic.list_departments'))


# ----------------- 4. PROGRAMS -----------------
@academic_bp.route('/programs')
@login_required
def list_programs():
    page = request.args.get('page', 1, type=int)
    programs = Program.query.paginate(page=page, per_page=10)
    return render_template('crud/list.html', title='Academic Programs', items=programs,
                           columns=[('ID', 'id'), ('Name', 'name'), ('Code', 'code'), ('Degree', 'degree_type'), ('Credits', 'total_credit_hours')],
                           create_url=url_for('academic.create_program'), edit_endpoint='academic.edit_program', delete_endpoint='academic.delete_program')

@academic_bp.route('/programs/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_program():
    form = ProgramForm()
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    if form.validate_on_submit():
        prog = Program(name=form.name.data, code=form.code.data.upper(), department_id=form.department_id.data, degree_type=form.degree_type.data, total_credit_hours=form.total_credit_hours.data, duration_years=form.duration_years.data)
        db.session.add(prog)
        db.session.commit()
        flash(f'Program "{prog.name}" created successfully!', 'success')
        return redirect(url_for('academic.list_programs'))
    return render_template('crud/form.html', title='Add Program', form=form, back_url=url_for('academic.list_programs'))

@academic_bp.route('/programs/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_program(id):
    prog = Program.query.get_or_404(id)
    form = ProgramForm(obj=prog)
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    if form.validate_on_submit():
        form.populate_obj(prog)
        prog.code = form.code.data.upper()
        db.session.commit()
        flash(f'Program "{prog.name}" updated successfully!', 'success')
        return redirect(url_for('academic.list_programs'))
    return render_template('crud/form.html', title='Edit Program', form=form, back_url=url_for('academic.list_programs'))

@academic_bp.route('/programs/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_program(id):
    prog = Program.query.get_or_404(id)
    db.session.delete(prog)
    db.session.commit()
    flash('Program deleted.', 'info')
    return redirect(url_for('academic.list_programs'))


# ----------------- 5. ACADEMIC YEARS -----------------
@academic_bp.route('/years')
@login_required
def list_years():
    years = AcademicYear.query.order_by(AcademicYear.start_date.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Academic Years', items=years,
                           columns=[('ID', 'id'), ('Year', 'year_name'), ('Start Date', 'start_date'), ('End Date', 'end_date'), ('Current', 'is_current')],
                           create_url=url_for('academic.create_year'), edit_endpoint='academic.edit_year', delete_endpoint='academic.delete_year')

@academic_bp.route('/years/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_year():
    form = AcademicYearForm()
    if form.validate_on_submit():
        year = AcademicYear(year_name=form.year_name.data, start_date=form.start_date.data, end_date=form.end_date.data, is_current=form.is_current.data)
        db.session.add(year)
        db.session.commit()
        flash(f'Academic Year "{year.year_name}" saved!', 'success')
        return redirect(url_for('academic.list_years'))
    return render_template('crud/form.html', title='Add Academic Year', form=form, back_url=url_for('academic.list_years'))

@academic_bp.route('/years/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_year(id):
    year = AcademicYear.query.get_or_404(id)
    form = AcademicYearForm(obj=year)
    if form.validate_on_submit():
        form.populate_obj(year)
        db.session.commit()
        flash(f'Academic Year updated!', 'success')
        return redirect(url_for('academic.list_years'))
    return render_template('crud/form.html', title='Edit Academic Year', form=form, back_url=url_for('academic.list_years'))

@academic_bp.route('/years/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_year(id):
    year = AcademicYear.query.get_or_404(id)
    db.session.delete(year)
    db.session.commit()
    flash('Academic Year deleted.', 'info')
    return redirect(url_for('academic.list_years'))


# ----------------- 6. SEMESTERS -----------------
@academic_bp.route('/semesters')
@login_required
def list_semesters():
    semesters = Semester.query.order_by(Semester.start_date.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Semesters', items=semesters,
                           columns=[('ID', 'id'), ('Name', 'name'), ('Start Date', 'start_date'), ('End Date', 'end_date'), ('Is Active', 'is_active')],
                           create_url=url_for('academic.create_semester'), edit_endpoint='academic.edit_semester', delete_endpoint='academic.delete_semester')

@academic_bp.route('/semesters/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_semester():
    form = SemesterForm()
    form.academic_year_id.choices = [(y.id, y.year_name) for y in AcademicYear.query.all()]
    if form.validate_on_submit():
        sem = Semester(name=form.name.data, academic_year_id=form.academic_year_id.data, start_date=form.start_date.data, end_date=form.end_date.data, is_active=form.is_active.data)
        db.session.add(sem)
        db.session.commit()
        flash(f'Semester "{sem.name}" created!', 'success')
        return redirect(url_for('academic.list_semesters'))
    return render_template('crud/form.html', title='Add Semester', form=form, back_url=url_for('academic.list_semesters'))

@academic_bp.route('/semesters/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_semester(id):
    sem = Semester.query.get_or_404(id)
    form = SemesterForm(obj=sem)
    form.academic_year_id.choices = [(y.id, y.year_name) for y in AcademicYear.query.all()]
    if form.validate_on_submit():
        form.populate_obj(sem)
        db.session.commit()
        flash('Semester updated!', 'success')
        return redirect(url_for('academic.list_semesters'))
    return render_template('crud/form.html', title='Edit Semester', form=form, back_url=url_for('academic.list_semesters'))

@academic_bp.route('/semesters/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_semester(id):
    sem = Semester.query.get_or_404(id)
    db.session.delete(sem)
    db.session.commit()
    flash('Semester deleted.', 'info')
    return redirect(url_for('academic.list_semesters'))


# ----------------- 7. COURSES -----------------
@academic_bp.route('/courses')
@login_required
def list_courses():
    search = request.args.get('search', '').strip()
    query = Course.query
    if search:
        query = query.filter(Course.code.ilike(f'%{search}%') | Course.title.ilike(f'%{search}%'))
    courses = query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Courses', items=courses,
                            columns=[('ID', 'id'), ('Code', 'code'), ('Title', 'title'), ('Department', 'department_name'), ('Credits', 'credit_hours')],
                            create_url=url_for('academic.create_course'), edit_endpoint='academic.edit_course', delete_endpoint='academic.delete_course')

@academic_bp.route('/courses/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_course():
    form = CourseForm()
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    if form.validate_on_submit():
        course = Course(code=form.code.data.upper(), title=form.title.data, credit_hours=form.credit_hours.data, department_id=form.department_id.data, description=form.description.data)
        db.session.add(course)
        db.session.commit()
        flash(f'Course "{course.code}" created successfully!', 'success')
        return redirect(url_for('academic.list_courses'))
    return render_template('crud/form.html', title='Add Course', form=form, back_url=url_for('academic.list_courses'))

@academic_bp.route('/courses/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_course(id):
    course = Course.query.get_or_404(id)
    form = CourseForm(obj=course)
    form.department_id.choices = [(d.id, d.name) for d in Department.query.all()]
    if form.validate_on_submit():
        form.populate_obj(course)
        course.code = form.code.data.upper()
        db.session.commit()
        flash(f'Course "{course.code}" updated successfully!', 'success')
        return redirect(url_for('academic.list_courses'))
    return render_template('crud/form.html', title='Edit Course', form=form, back_url=url_for('academic.list_courses'))

@academic_bp.route('/courses/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_course(id):
    course = Course.query.get_or_404(id)
    db.session.delete(course)
    db.session.commit()
    flash('Course deleted.', 'info')
    return redirect(url_for('academic.list_courses'))


# ----------------- 8. COURSE PREREQUISITES -----------------
@academic_bp.route('/prerequisites')
@login_required
def list_prerequisites():
    prereqs = CoursePrerequisite.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Course Prerequisites', items=prereqs,
                           columns=[('ID', 'id'), ('Target Course', 'course_display'), ('Required Prerequisite', 'prerequisite_display'), ('Min Grade to Pass', 'minimum_grade')],
                           create_url=url_for('academic.create_prerequisite'), edit_endpoint='academic.edit_prerequisite', delete_endpoint='academic.delete_prerequisite')

@academic_bp.route('/prerequisites/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_prerequisite():
    form = CoursePrerequisiteForm()
    courses = Course.query.all()
    form.course_id.choices = [(c.id, f"{c.code} - {c.title}") for c in courses]
    form.prerequisite_id.choices = [(c.id, f"{c.code} - {c.title}") for c in courses]
    if form.validate_on_submit():
        if form.course_id.data == form.prerequisite_id.data:
            flash('A course cannot be a prerequisite of itself.', 'danger')
        else:
            prereq = CoursePrerequisite(course_id=form.course_id.data, prerequisite_id=form.prerequisite_id.data, minimum_grade=form.minimum_grade.data)
            db.session.add(prereq)
            db.session.commit()
            flash('Prerequisite assigned successfully!', 'success')
            return redirect(url_for('academic.list_prerequisites'))
    return render_template('crud/form.html', title='Assign Prerequisite', form=form, back_url=url_for('academic.list_prerequisites'))

@academic_bp.route('/prerequisites/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_prerequisite(id):
    prereq = CoursePrerequisite.query.get_or_404(id)
    form = CoursePrerequisiteForm(obj=prereq)
    courses = Course.query.all()
    form.course_id.choices = [(c.id, f"{c.code} - {c.title}") for c in courses]
    form.prerequisite_id.choices = [(c.id, f"{c.code} - {c.title}") for c in courses]
    if form.validate_on_submit():
        form.populate_obj(prereq)
        db.session.commit()
        flash('Prerequisite updated!', 'success')
        return redirect(url_for('academic.list_prerequisites'))
    return render_template('crud/form.html', title='Edit Prerequisite', form=form, back_url=url_for('academic.list_prerequisites'))

@academic_bp.route('/prerequisites/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_prerequisite(id):
    prereq = CoursePrerequisite.query.get_or_404(id)
    db.session.delete(prereq)
    db.session.commit()
    flash('Prerequisite removed.', 'info')
    return redirect(url_for('academic.list_prerequisites'))
