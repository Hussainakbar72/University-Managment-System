from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.utils.decorators import admin_required, teacher_required
from app.models.academic import Campus, Course, Semester
from app.models.auth import Student, Instructor
from app.models.enrollment import (
    Classroom, CourseSection, SectionSchedule, Enrollment, Attendance
)
from app.forms.enrollment_forms import (
    ClassroomForm, CourseSectionForm, SectionScheduleForm, EnrollmentForm, AttendanceForm
)

enrollment_mgmt_bp = Blueprint('enrollment_mgmt', __name__, url_prefix='/classes')

# ----------------- 1. CLASSROOMS -----------------
@enrollment_mgmt_bp.route('/classrooms')
@login_required
def list_classrooms():
    classrooms = Classroom.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Classrooms & Lecture Halls', items=classrooms,
                           columns=[('ID', 'id'), ('Building', 'building_name'), ('Room #', 'room_number'), ('Capacity', 'capacity'), ('Type', 'room_type')],
                           create_url=url_for('enrollment_mgmt.create_classroom'), edit_endpoint='enrollment_mgmt.edit_classroom', delete_endpoint='enrollment_mgmt.delete_classroom')

@enrollment_mgmt_bp.route('/classrooms/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_classroom():
    form = ClassroomForm()
    form.campus_id.choices = [(c.id, c.name) for c in Campus.query.all()]
    if form.validate_on_submit():
        cr = Classroom(campus_id=form.campus_id.data, building_name=form.building_name.data, room_number=form.room_number.data, capacity=form.capacity.data, room_type=form.room_type.data)
        db.session.add(cr)
        db.session.commit()
        flash(f'Classroom "{cr.room_number}" added!', 'success')
        return redirect(url_for('enrollment_mgmt.list_classrooms'))
    return render_template('crud/form.html', title='Add Classroom', form=form, back_url=url_for('enrollment_mgmt.list_classrooms'))

@enrollment_mgmt_bp.route('/classrooms/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_classroom(id):
    cr = Classroom.query.get_or_404(id)
    form = ClassroomForm(obj=cr)
    form.campus_id.choices = [(c.id, c.name) for c in Campus.query.all()]
    if form.validate_on_submit():
        form.populate_obj(cr)
        db.session.commit()
        flash('Classroom updated!', 'success')
        return redirect(url_for('enrollment_mgmt.list_classrooms'))
    return render_template('crud/form.html', title='Edit Classroom', form=form, back_url=url_for('enrollment_mgmt.list_classrooms'))

@enrollment_mgmt_bp.route('/classrooms/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_classroom(id):
    cr = Classroom.query.get_or_404(id)
    db.session.delete(cr)
    db.session.commit()
    flash('Classroom deleted.', 'info')
    return redirect(url_for('enrollment_mgmt.list_classrooms'))


# ----------------- 2. COURSE SECTIONS -----------------
@enrollment_mgmt_bp.route('/sections')
@login_required
def list_sections():
    sections = CourseSection.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Course Sections', items=sections,
                           columns=[('ID', 'id'), ('Section', 'section_name'), ('Course ID', 'course_id'), ('Semester ID', 'semester_id'), ('Max Capacity', 'max_capacity')],
                           create_url=url_for('enrollment_mgmt.create_section'), edit_endpoint='enrollment_mgmt.edit_section', delete_endpoint='enrollment_mgmt.delete_section')

@enrollment_mgmt_bp.route('/sections/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_section():
    form = CourseSectionForm()
    form.course_id.choices = [(c.id, f"{c.code} - {c.title}") for c in Course.query.all()]
    form.semester_id.choices = [(s.id, s.name) for s in Semester.query.all()]
    instructors = [(0, '-- No Instructor Assigned --')] + [(i.id, f"{i.employee_id} ({i.user.full_name if i.user else ''})") for i in Instructor.query.all()]
    form.instructor_id.choices = instructors
    if form.validate_on_submit():
        ins_id = form.instructor_id.data if form.instructor_id.data != 0 else None
        section = CourseSection(section_name=form.section_name.data.upper(), course_id=form.course_id.data, semester_id=form.semester_id.data, instructor_id=ins_id, max_capacity=form.max_capacity.data)
        db.session.add(section)
        db.session.commit()
        flash(f'Section "{section.section_name}" created!', 'success')
        return redirect(url_for('enrollment_mgmt.list_sections'))
    return render_template('crud/form.html', title='Create Course Section', form=form, back_url=url_for('enrollment_mgmt.list_sections'))

@enrollment_mgmt_bp.route('/sections/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_section(id):
    section = CourseSection.query.get_or_404(id)
    form = CourseSectionForm(obj=section)
    form.course_id.choices = [(c.id, f"{c.code} - {c.title}") for c in Course.query.all()]
    form.semester_id.choices = [(s.id, s.name) for s in Semester.query.all()]
    instructors = [(0, '-- No Instructor Assigned --')] + [(i.id, f"{i.employee_id} ({i.user.full_name if i.user else ''})") for i in Instructor.query.all()]
    form.instructor_id.choices = instructors
    if request.method == 'GET' and not section.instructor_id:
        form.instructor_id.data = 0
    if form.validate_on_submit():
        form.populate_obj(section)
        section.section_name = form.section_name.data.upper()
        section.instructor_id = form.instructor_id.data if form.instructor_id.data != 0 else None
        db.session.commit()
        flash('Section updated!', 'success')
        return redirect(url_for('enrollment_mgmt.list_sections'))
    return render_template('crud/form.html', title='Edit Section', form=form, back_url=url_for('enrollment_mgmt.list_sections'))

@enrollment_mgmt_bp.route('/sections/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_section(id):
    section = CourseSection.query.get_or_404(id)
    db.session.delete(section)
    db.session.commit()
    flash('Section deleted.', 'info')
    return redirect(url_for('enrollment_mgmt.list_sections'))


# ----------------- 3. SECTION SCHEDULES -----------------
@enrollment_mgmt_bp.route('/schedules')
@login_required
def list_schedules():
    query = SectionSchedule.query
    if current_user.has_role('STUDENT'):
        if current_user.student_profile:
            enrolled_section_ids = [e.section_id for e in current_user.student_profile.enrollments]
            query = query.filter(SectionSchedule.section_id.in_(enrolled_section_ids))
        else:
            query = query.filter(SectionSchedule.id == -1)
    elif current_user.has_role('TEACHER'):
        if current_user.instructor_profile:
            taught_section_ids = [s.id for s in current_user.instructor_profile.sections]
            query = query.filter(SectionSchedule.section_id.in_(taught_section_ids))
        else:
            query = query.filter(SectionSchedule.id == -1)

    schedules = query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Timetable & Class Schedules', items=schedules,
                           columns=[('ID', 'id'), ('Class Section', 'schedule_section'), ('Classroom', 'classroom_display'), ('Day', 'day_of_week'), ('Start', 'start_time'), ('End', 'end_time')],
                           create_url=url_for('enrollment_mgmt.create_schedule'), edit_endpoint='enrollment_mgmt.edit_schedule', delete_endpoint='enrollment_mgmt.delete_schedule')

@enrollment_mgmt_bp.route('/schedules/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_schedule():
    form = SectionScheduleForm()
    form.section_id.choices = [(s.id, f"Section {s.section_name} ({s.course.code if s.course else s.course_id})") for s in CourseSection.query.all()]
    form.classroom_id.choices = [(0, '-- Unassigned --')] + [(c.id, f"{c.building_name} {c.room_number}") for c in Classroom.query.all()]
    if form.validate_on_submit():
        cr_id = form.classroom_id.data if form.classroom_id.data != 0 else None
        sched = SectionSchedule(section_id=form.section_id.data, classroom_id=cr_id, day_of_week=form.day_of_week.data, start_time=form.start_time.data, end_time=form.end_time.data)
        db.session.add(sched)
        db.session.commit()
        flash('Schedule slot created!', 'success')
        return redirect(url_for('enrollment_mgmt.list_schedules'))
    return render_template('crud/form.html', title='Add Schedule Slot', form=form, back_url=url_for('enrollment_mgmt.list_schedules'))

@enrollment_mgmt_bp.route('/schedules/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_schedule(id):
    sched = SectionSchedule.query.get_or_404(id)
    form = SectionScheduleForm(obj=sched)
    form.section_id.choices = [(s.id, f"Section {s.section_name} ({s.course.code if s.course else s.course_id})") for s in CourseSection.query.all()]
    form.classroom_id.choices = [(0, '-- Unassigned --')] + [(c.id, f"{c.building_name} {c.room_number}") for c in Classroom.query.all()]
    if request.method == 'GET' and not sched.classroom_id:
        form.classroom_id.data = 0
    if form.validate_on_submit():
        form.populate_obj(sched)
        sched.classroom_id = form.classroom_id.data if form.classroom_id.data != 0 else None
        db.session.commit()
        flash('Schedule slot updated!', 'success')
        return redirect(url_for('enrollment_mgmt.list_schedules'))
    return render_template('crud/form.html', title='Edit Schedule Slot', form=form, back_url=url_for('enrollment_mgmt.list_schedules'))

@enrollment_mgmt_bp.route('/schedules/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_schedule(id):
    sched = SectionSchedule.query.get_or_404(id)
    db.session.delete(sched)
    db.session.commit()
    flash('Schedule slot removed.', 'info')
    return redirect(url_for('enrollment_mgmt.list_schedules'))


# ----------------- 4. ENROLLMENTS -----------------
@enrollment_mgmt_bp.route('/enrollments')
@login_required
def list_enrollments():
    query = Enrollment.query
    if current_user.has_role('STUDENT') and current_user.student_profile:
        query = query.filter_by(student_id=current_user.student_profile.id)
    enrollments = query.order_by(Enrollment.id.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Course Enrollments', items=enrollments,
                           columns=[('ID', 'id'), ('Student Reg #', 'student_reg_number'), ('Course', 'course_name'), ('Section', 'section_title'), ('Date', 'enrolled_at'), ('Status', 'status')],
                           create_url=url_for('enrollment_mgmt.create_enrollment'), edit_endpoint='enrollment_mgmt.edit_enrollment', delete_endpoint='enrollment_mgmt.delete_enrollment')

@enrollment_mgmt_bp.route('/enrollments/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_enrollment():
    form = EnrollmentForm()
    form.student_id.choices = [(s.id, s.registration_number) for s in Student.query.all()]
    form.section_id.choices = [(sec.id, f"{sec.course.code if sec.course else ''} - Sec {sec.section_name}") for sec in CourseSection.query.all()]
    if form.validate_on_submit():
        existing = Enrollment.query.filter_by(student_id=form.student_id.data, section_id=form.section_id.data).first()
        if existing:
            flash('Student is already enrolled in this section.', 'warning')
        else:
            enr = Enrollment(student_id=form.student_id.data, section_id=form.section_id.data, status=form.status.data)
            db.session.add(enr)
            db.session.commit()
            flash('Student enrolled successfully!', 'success')
            return redirect(url_for('enrollment_mgmt.list_enrollments'))
    return render_template('crud/form.html', title='Enroll Student', form=form, back_url=url_for('enrollment_mgmt.list_enrollments'))

@enrollment_mgmt_bp.route('/enrollments/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_enrollment(id):
    enr = Enrollment.query.get_or_404(id)
    form = EnrollmentForm(obj=enr)
    form.student_id.choices = [(s.id, s.registration_number) for s in Student.query.all()]
    form.section_id.choices = [(sec.id, f"{sec.course.code if sec.course else ''} - Sec {sec.section_name}") for sec in CourseSection.query.all()]
    if form.validate_on_submit():
        form.populate_obj(enr)
        db.session.commit()
        flash('Enrollment status updated!', 'success')
        return redirect(url_for('enrollment_mgmt.list_enrollments'))
    return render_template('crud/form.html', title='Edit Enrollment', form=form, back_url=url_for('enrollment_mgmt.list_enrollments'))

@enrollment_mgmt_bp.route('/enrollments/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_enrollment(id):
    enr = Enrollment.query.get_or_404(id)
    db.session.delete(enr)
    db.session.commit()
    flash('Enrollment deleted.', 'info')
    return redirect(url_for('enrollment_mgmt.list_enrollments'))


# ----------------- 5. ATTENDANCE -----------------
@enrollment_mgmt_bp.route('/attendance')
@login_required
def list_attendance():
    query = Attendance.query
    if current_user.has_role('STUDENT') and current_user.student_profile:
        student_enr_ids = [e.id for e in current_user.student_profile.enrollments]
        query = query.filter(Attendance.enrollment_id.in_(student_enr_ids))
    records = query.order_by(Attendance.date.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Attendance Logs', items=records,
                           columns=[('ID', 'id'), ('Student Reg #', 'student_reg'), ('Course', 'course_code'), ('Date', 'date'), ('Status', 'status'), ('Remarks', 'remarks')],
                           create_url=url_for('enrollment_mgmt.create_attendance'), edit_endpoint='enrollment_mgmt.edit_attendance', delete_endpoint='enrollment_mgmt.delete_attendance')

@enrollment_mgmt_bp.route('/attendance/add', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_attendance():
    form = AttendanceForm()
    form.enrollment_id.choices = [(e.id, f"Enr #{e.id} ({e.student.registration_number if e.student else ''} - {e.section.section_name if e.section else ''})") for e in Enrollment.query.all()]
    schedules = [(0, '-- None --')] + [(s.id, f"{s.day_of_week} ({s.start_time})") for s in SectionSchedule.query.all()]
    form.schedule_id.choices = schedules
    if form.validate_on_submit():
        sch_id = form.schedule_id.data if form.schedule_id.data != 0 else None
        att = Attendance(enrollment_id=form.enrollment_id.data, schedule_id=sch_id, date=form.date.data, status=form.status.data, remarks=form.remarks.data)
        db.session.add(att)
        db.session.commit()
        flash('Attendance record saved!', 'success')
        return redirect(url_for('enrollment_mgmt.list_attendance'))
    return render_template('crud/form.html', title='Record Attendance', form=form, back_url=url_for('enrollment_mgmt.list_attendance'))

@enrollment_mgmt_bp.route('/attendance/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_attendance(id):
    att = Attendance.query.get_or_404(id)
    form = AttendanceForm(obj=att)
    form.enrollment_id.choices = [(e.id, f"Enr #{e.id} ({e.student.registration_number if e.student else ''})") for e in Enrollment.query.all()]
    schedules = [(0, '-- None --')] + [(s.id, f"{s.day_of_week} ({s.start_time})") for s in SectionSchedule.query.all()]
    form.schedule_id.choices = schedules
    if request.method == 'GET' and not att.schedule_id:
        form.schedule_id.data = 0
    if form.validate_on_submit():
        form.populate_obj(att)
        att.schedule_id = form.schedule_id.data if form.schedule_id.data != 0 else None
        db.session.commit()
        flash('Attendance record updated!', 'success')
        return redirect(url_for('enrollment_mgmt.list_attendance'))
    return render_template('crud/form.html', title='Edit Attendance', form=form, back_url=url_for('enrollment_mgmt.list_attendance'))

@enrollment_mgmt_bp.route('/attendance/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_attendance(id):
    att = Attendance.query.get_or_404(id)
    db.session.delete(att)
    db.session.commit()
    flash('Attendance record removed.', 'info')
    return redirect(url_for('enrollment_mgmt.list_attendance'))
