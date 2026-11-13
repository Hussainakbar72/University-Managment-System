from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.utils.decorators import admin_required, teacher_required
from app.models.academic import Course, Semester
from app.models.auth import Student
from app.models.enrollment import CourseSection, Enrollment, Classroom
from app.models.examination import (
    Assessment, AssessmentResult, Exam, ExamRoom, ExamSeating, Grade, Transcript
)
from app.forms.exam_forms import (
    AssessmentForm, AssessmentResultForm, ExamForm, ExamRoomForm,
    ExamSeatingForm, GradeForm, TranscriptForm
)

exams_mgmt_bp = Blueprint('exams_mgmt', __name__, url_prefix='/exams')

# ----------------- 1. ASSESSMENTS -----------------
@exams_mgmt_bp.route('/assessments')
@login_required
def list_assessments():
    items = Assessment.query.order_by(Assessment.id.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Continuous Assessments', items=items,
                           columns=[('ID', 'id'), ('Title', 'title'), ('Type', 'assessment_type'), ('Max Marks', 'max_marks'), ('Weightage %', 'weightage'), ('Due Date', 'due_date')],
                           create_url=url_for('exams_mgmt.create_assessment'), edit_endpoint='exams_mgmt.edit_assessment', delete_endpoint='exams_mgmt.delete_assessment')

@exams_mgmt_bp.route('/assessments/add', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_assessment():
    form = AssessmentForm()
    form.section_id.choices = [(s.id, f"{s.course.code if s.course else ''} - Sec {s.section_name}") for s in CourseSection.query.all()]
    if form.validate_on_submit():
        item = Assessment(section_id=form.section_id.data, title=form.title.data, assessment_type=form.assessment_type.data, max_marks=form.max_marks.data, weightage=form.weightage.data, due_date=form.due_date.data)
        db.session.add(item)
        db.session.commit()
        flash(f'Assessment "{item.title}" created!', 'success')
        return redirect(url_for('exams_mgmt.list_assessments'))
    return render_template('crud/form.html', title='Create Assessment', form=form, back_url=url_for('exams_mgmt.list_assessments'))

@exams_mgmt_bp.route('/assessments/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_assessment(id):
    item = Assessment.query.get_or_404(id)
    form = AssessmentForm(obj=item)
    form.section_id.choices = [(s.id, f"{s.course.code if s.course else ''} - Sec {s.section_name}") for s in CourseSection.query.all()]
    if form.validate_on_submit():
        form.populate_obj(item)
        db.session.commit()
        flash('Assessment updated!', 'success')
        return redirect(url_for('exams_mgmt.list_assessments'))
    return render_template('crud/form.html', title='Edit Assessment', form=form, back_url=url_for('exams_mgmt.list_assessments'))

@exams_mgmt_bp.route('/assessments/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_assessment(id):
    item = Assessment.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Assessment deleted.', 'info')
    return redirect(url_for('exams_mgmt.list_assessments'))


# ----------------- 2. ASSESSMENT RESULTS -----------------
@exams_mgmt_bp.route('/assessment-results')
@login_required
def list_assessment_results():
    results = AssessmentResult.query.order_by(AssessmentResult.id.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Assessment Results', items=results,
                           columns=[('ID', 'id'), ('Assessment ID', 'assessment_id'), ('Enrollment ID', 'enrollment_id'), ('Score', 'marks_obtained'), ('Graded At', 'graded_at')],
                           create_url=url_for('exams_mgmt.create_assessment_result'), edit_endpoint='exams_mgmt.edit_assessment_result', delete_endpoint='exams_mgmt.delete_assessment_result')

@exams_mgmt_bp.route('/assessment-results/add', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_assessment_result():
    form = AssessmentResultForm()
    form.assessment_id.choices = [(a.id, f"{a.title} ({a.assessment_type})") for a in Assessment.query.all()]
    form.enrollment_id.choices = [(e.id, f"Enr #{e.id} ({e.student.registration_number if e.student else ''})") for e in Enrollment.query.all()]
    if form.validate_on_submit():
        res = AssessmentResult(assessment_id=form.assessment_id.data, enrollment_id=form.enrollment_id.data, marks_obtained=form.marks_obtained.data, feedback=form.feedback.data)
        db.session.add(res)
        db.session.commit()
        flash('Assessment marks recorded!', 'success')
        return redirect(url_for('exams_mgmt.list_assessment_results'))
    return render_template('crud/form.html', title='Record Assessment Result', form=form, back_url=url_for('exams_mgmt.list_assessment_results'))

@exams_mgmt_bp.route('/assessment-results/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_assessment_result(id):
    res = AssessmentResult.query.get_or_404(id)
    form = AssessmentResultForm(obj=res)
    form.assessment_id.choices = [(a.id, f"{a.title} ({a.assessment_type})") for a in Assessment.query.all()]
    form.enrollment_id.choices = [(e.id, f"Enr #{e.id} ({e.student.registration_number if e.student else ''})") for e in Enrollment.query.all()]
    if form.validate_on_submit():
        form.populate_obj(res)
        db.session.commit()
        flash('Result updated!', 'success')
        return redirect(url_for('exams_mgmt.list_assessment_results'))
    return render_template('crud/form.html', title='Edit Result', form=form, back_url=url_for('exams_mgmt.list_assessment_results'))

@exams_mgmt_bp.route('/assessment-results/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_assessment_result(id):
    res = AssessmentResult.query.get_or_404(id)
    db.session.delete(res)
    db.session.commit()
    flash('Assessment result deleted.', 'info')
    return redirect(url_for('exams_mgmt.list_assessment_results'))


# ----------------- 3. EXAMS (MID/FINAL) -----------------
@exams_mgmt_bp.route('/schedules')
@login_required
def list_exams():
    exams = Exam.query.order_by(Exam.exam_date.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Examination Timetable', items=exams,
                           columns=[('ID', 'id'), ('Course ID', 'course_id'), ('Type', 'exam_type'), ('Date', 'exam_date'), ('Start', 'start_time'), ('Duration', 'duration_minutes')],
                           create_url=url_for('exams_mgmt.create_exam'), edit_endpoint='exams_mgmt.edit_exam', delete_endpoint='exams_mgmt.delete_exam')

@exams_mgmt_bp.route('/schedules/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_exam():
    form = ExamForm()
    form.course_id.choices = [(c.id, f"{c.code} - {c.title}") for c in Course.query.all()]
    form.semester_id.choices = [(s.id, s.name) for s in Semester.query.all()]
    if form.validate_on_submit():
        exam = Exam(course_id=form.course_id.data, semester_id=form.semester_id.data, exam_type=form.exam_type.data, exam_date=form.exam_date.data, start_time=form.start_time.data, duration_minutes=form.duration_minutes.data, total_marks=form.total_marks.data)
        db.session.add(exam)
        db.session.commit()
        flash('Exam scheduled successfully!', 'success')
        return redirect(url_for('exams_mgmt.list_exams'))
    return render_template('crud/form.html', title='Schedule Exam', form=form, back_url=url_for('exams_mgmt.list_exams'))

@exams_mgmt_bp.route('/schedules/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_exam(id):
    exam = Exam.query.get_or_404(id)
    form = ExamForm(obj=exam)
    form.course_id.choices = [(c.id, f"{c.code} - {c.title}") for c in Course.query.all()]
    form.semester_id.choices = [(s.id, s.name) for s in Semester.query.all()]
    if form.validate_on_submit():
        form.populate_obj(exam)
        db.session.commit()
        flash('Exam schedule updated!', 'success')
        return redirect(url_for('exams_mgmt.list_exams'))
    return render_template('crud/form.html', title='Edit Exam Schedule', form=form, back_url=url_for('exams_mgmt.list_exams'))

@exams_mgmt_bp.route('/schedules/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_exam(id):
    exam = Exam.query.get_or_404(id)
    db.session.delete(exam)
    db.session.commit()
    flash('Exam removed.', 'info')
    return redirect(url_for('exams_mgmt.list_exams'))


# ----------------- 4. EXAM ROOMS -----------------
@exams_mgmt_bp.route('/rooms')
@login_required
def list_exam_rooms():
    rooms = ExamRoom.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Exam Hall Allocations', items=rooms,
                           columns=[('ID', 'id'), ('Exam ID', 'exam_id'), ('Classroom ID', 'classroom_id'), ('Invigilator', 'invigilator_name')],
                           create_url=url_for('exams_mgmt.create_exam_room'), edit_endpoint='exams_mgmt.edit_exam_room', delete_endpoint='exams_mgmt.delete_exam_room')

@exams_mgmt_bp.route('/rooms/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_exam_room():
    form = ExamRoomForm()
    form.exam_id.choices = [(e.id, f"Exam #{e.id} ({e.exam_type} - Course {e.course_id})") for e in Exam.query.all()]
    form.classroom_id.choices = [(c.id, f"{c.building_name} {c.room_number}") for c in Classroom.query.all()]
    if form.validate_on_submit():
        er = ExamRoom(exam_id=form.exam_id.data, classroom_id=form.classroom_id.data, invigilator_name=form.invigilator_name.data)
        db.session.add(er)
        db.session.commit()
        flash('Exam room allocation saved!', 'success')
        return redirect(url_for('exams_mgmt.list_exam_rooms'))
    return render_template('crud/form.html', title='Allocate Exam Room', form=form, back_url=url_for('exams_mgmt.list_exam_rooms'))

@exams_mgmt_bp.route('/rooms/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_exam_room(id):
    er = ExamRoom.query.get_or_404(id)
    form = ExamRoomForm(obj=er)
    form.exam_id.choices = [(e.id, f"Exam #{e.id} ({e.exam_type} - Course {e.course_id})") for e in Exam.query.all()]
    form.classroom_id.choices = [(c.id, f"{c.building_name} {c.room_number}") for c in Classroom.query.all()]
    if form.validate_on_submit():
        form.populate_obj(er)
        db.session.commit()
        flash('Exam room updated!', 'success')
        return redirect(url_for('exams_mgmt.list_exam_rooms'))
    return render_template('crud/form.html', title='Edit Exam Room', form=form, back_url=url_for('exams_mgmt.list_exam_rooms'))

@exams_mgmt_bp.route('/rooms/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_exam_room(id):
    er = ExamRoom.query.get_or_404(id)
    db.session.delete(er)
    db.session.commit()
    flash('Exam room allocation removed.', 'info')
    return redirect(url_for('exams_mgmt.list_exam_rooms'))


# ----------------- 5. EXAM SEATING -----------------
@exams_mgmt_bp.route('/seating')
@login_required
def list_exam_seating():
    seats = ExamSeating.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Exam Seating Plan', items=seats,
                           columns=[('ID', 'id'), ('Room ID', 'exam_room_id'), ('Enrollment ID', 'enrollment_id'), ('Seat #', 'seat_number'), ('Attended', 'is_attended')],
                           create_url=url_for('exams_mgmt.create_exam_seating'), edit_endpoint='exams_mgmt.edit_exam_seating', delete_endpoint='exams_mgmt.delete_exam_seating')

@exams_mgmt_bp.route('/seating/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_exam_seating():
    form = ExamSeatingForm()
    form.exam_room_id.choices = [(r.id, f"Exam Room #{r.id} (Room {r.classroom_id})") for r in ExamRoom.query.all()]
    form.enrollment_id.choices = [(e.id, f"Enr #{e.id} ({e.student.registration_number if e.student else ''})") for e in Enrollment.query.all()]
    if form.validate_on_submit():
        seat = ExamSeating(exam_room_id=form.exam_room_id.data, enrollment_id=form.enrollment_id.data, seat_number=form.seat_number.data, is_attended=form.is_attended.data)
        db.session.add(seat)
        db.session.commit()
        flash('Seat assigned successfully!', 'success')
        return redirect(url_for('exams_mgmt.list_exam_seating'))
    return render_template('crud/form.html', title='Assign Seat', form=form, back_url=url_for('exams_mgmt.list_exam_seating'))

@exams_mgmt_bp.route('/seating/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_exam_seating(id):
    seat = ExamSeating.query.get_or_404(id)
    form = ExamSeatingForm(obj=seat)
    form.exam_room_id.choices = [(r.id, f"Exam Room #{r.id} (Room {r.classroom_id})") for r in ExamRoom.query.all()]
    form.enrollment_id.choices = [(e.id, f"Enr #{e.id} ({e.student.registration_number if e.student else ''})") for e in Enrollment.query.all()]
    if form.validate_on_submit():
        form.populate_obj(seat)
        db.session.commit()
        flash('Seat assignment updated!', 'success')
        return redirect(url_for('exams_mgmt.list_exam_seating'))
    return render_template('crud/form.html', title='Edit Seating', form=form, back_url=url_for('exams_mgmt.list_exam_seating'))

@exams_mgmt_bp.route('/seating/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_exam_seating(id):
    seat = ExamSeating.query.get_or_404(id)
    db.session.delete(seat)
    db.session.commit()
    flash('Seating removed.', 'info')
    return redirect(url_for('exams_mgmt.list_exam_seating'))


# ----------------- 6. GRADES -----------------
@exams_mgmt_bp.route('/grades')
@login_required
def list_grades():
    query = Grade.query
    if current_user.has_role('STUDENT'):
        if current_user.student_profile:
            query = query.join(Enrollment).filter(Enrollment.student_id == current_user.student_profile.id)
        else:
            query = query.filter(Grade.id == -1)

    grades = query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    columns = [('ID', 'id'), ('Student Reg', 'student_reg'), ('Course', 'course_name'), ('Total Score', 'total_score'), ('Letter Grade', 'letter_grade'), ('GPA', 'grade_points')]
    return render_template('crud/list.html', title='Final Course Grades', items=grades,
                           columns=columns,
                           create_url=url_for('exams_mgmt.create_grade'), edit_endpoint='exams_mgmt.edit_grade', delete_endpoint='exams_mgmt.delete_grade')

@exams_mgmt_bp.route('/grades/add', methods=['GET', 'POST'])
@login_required
@teacher_required
def create_grade():
    form = GradeForm()
    form.enrollment_id.choices = [(e.id, f"Enr #{e.id} ({e.student.registration_number if e.student else ''} - Sec {e.section_id})") for e in Enrollment.query.all()]
    if form.validate_on_submit():
        existing = Grade.query.filter_by(enrollment_id=form.enrollment_id.data).first()
        if existing:
            flash('Grade already submitted for this enrollment. Please edit existing grade.', 'warning')
        else:
            g = Grade(enrollment_id=form.enrollment_id.data, total_score=form.total_score.data, letter_grade=form.letter_grade.data, grade_points=form.grade_points.data)
            db.session.add(g)
            db.session.commit()
            flash('Final grade posted successfully!', 'success')
            return redirect(url_for('exams_mgmt.list_grades'))
    return render_template('crud/form.html', title='Submit Final Grade', form=form, back_url=url_for('exams_mgmt.list_grades'))

@exams_mgmt_bp.route('/grades/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@teacher_required
def edit_grade(id):
    g = Grade.query.get_or_404(id)
    form = GradeForm(obj=g)
    form.enrollment_id.choices = [(e.id, f"Enr #{e.id} ({e.student.registration_number if e.student else ''})") for e in Enrollment.query.all()]
    if form.validate_on_submit():
        form.populate_obj(g)
        db.session.commit()
        flash('Grade updated!', 'success')
        return redirect(url_for('exams_mgmt.list_grades'))
    return render_template('crud/form.html', title='Edit Grade', form=form, back_url=url_for('exams_mgmt.list_grades'))

@exams_mgmt_bp.route('/grades/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_grade(id):
    g = Grade.query.get_or_404(id)
    db.session.delete(g)
    db.session.commit()
    flash('Grade record deleted.', 'info')
    return redirect(url_for('exams_mgmt.list_grades'))


# ----------------- 7. TRANSCRIPTS -----------------
@exams_mgmt_bp.route('/transcripts')
@login_required
def list_transcripts():
    transcripts = Transcript.query.order_by(Transcript.issue_date.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Academic Transcripts', items=transcripts,
                           columns=[('ID', 'id'), ('Student ID', 'student_id'), ('Issue Date', 'issue_date'), ('Credits Earned', 'total_credits_earned'), ('CGPA', 'cumulative_gpa'), ('Remarks', 'remarks')],
                           create_url=url_for('exams_mgmt.create_transcript'), edit_endpoint='exams_mgmt.edit_transcript', delete_endpoint='exams_mgmt.delete_transcript')

@exams_mgmt_bp.route('/transcripts/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_transcript():
    form = TranscriptForm()
    form.student_id.choices = [(s.id, f"{s.registration_number} ({s.user.full_name if s.user else ''})") for s in Student.query.all()]
    if form.validate_on_submit():
        tr = Transcript(student_id=form.student_id.data, issue_date=form.issue_date.data, total_credits_earned=form.total_credits_earned.data, cumulative_gpa=form.cumulative_gpa.data, remarks=form.remarks.data)
        db.session.add(tr)
        db.session.commit()
        flash('Transcript generated successfully!', 'success')
        return redirect(url_for('exams_mgmt.list_transcripts'))
    return render_template('crud/form.html', title='Issue Transcript', form=form, back_url=url_for('exams_mgmt.list_transcripts'))

@exams_mgmt_bp.route('/transcripts/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_transcript(id):
    tr = Transcript.query.get_or_404(id)
    form = TranscriptForm(obj=tr)
    form.student_id.choices = [(s.id, f"{s.registration_number}") for s in Student.query.all()]
    if form.validate_on_submit():
        form.populate_obj(tr)
        db.session.commit()
        flash('Transcript record updated!', 'success')
        return redirect(url_for('exams_mgmt.list_transcripts'))
    return render_template('crud/form.html', title='Edit Transcript', form=form, back_url=url_for('exams_mgmt.list_transcripts'))

@exams_mgmt_bp.route('/transcripts/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_transcript(id):
    tr = Transcript.query.get_or_404(id)
    db.session.delete(tr)
    db.session.commit()
    flash('Transcript record deleted.', 'info')
    return redirect(url_for('exams_mgmt.list_transcripts'))
