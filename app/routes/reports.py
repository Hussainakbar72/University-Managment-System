from flask import Blueprint, render_template, request
from flask_login import login_required
from sqlalchemy import func
from app.extensions import db
from app.utils.decorators import admin_required
from app.models.auth import Student
from app.models.academic import Department, Program, Course, Semester
from app.models.enrollment import Enrollment, Attendance, CourseSection
from app.models.examination import Grade
from app.models.finance import StudentInvoice, Payment

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/students')
@login_required
@admin_required
def student_list_report():
    program_id = request.args.get('program_id', type=int)
    status = request.args.get('status', '').strip()
    query = Student.query
    if program_id:
        query = query.filter(Student.program_id == program_id)
    if status:
        query = query.filter(Student.status == status)
    students = query.all()
    programs = Program.query.all()
    return render_template('reports/students.html', students=students, programs=programs, selected_program=program_id, selected_status=status)

@reports_bp.route('/attendance')
@login_required
@admin_required
def attendance_report():
    section_id = request.args.get('section_id', type=int)
    sections = CourseSection.query.all()
    records = []
    summary = {}
    if section_id:
        enrollments = Enrollment.query.filter_by(section_id=section_id).all()
        for enr in enrollments:
            total = Attendance.query.filter_by(enrollment_id=enr.id).count()
            presents = Attendance.query.filter_by(enrollment_id=enr.id, status='Present').count()
            pct = round((presents / total * 100), 1) if total > 0 else 0.0
            records.append({
                'student': enr.student,
                'total': total,
                'presents': presents,
                'percentage': pct
            })
    return render_template('reports/attendance.html', sections=sections, selected_section=section_id, records=records)

@reports_bp.route('/enrollment')
@login_required
@admin_required
def enrollment_report():
    semester_id = request.args.get('semester_id', type=int)
    semesters = Semester.query.all()
    section_stats = []
    if semester_id:
        sections = CourseSection.query.filter_by(semester_id=semester_id).all()
        for sec in sections:
            count = Enrollment.query.filter_by(section_id=sec.id).count()
            section_stats.append({
                'course': sec.course,
                'section_name': sec.section_name,
                'instructor': sec.instructor,
                'enrolled_count': count,
                'max_capacity': sec.max_capacity
            })
    return render_template('reports/enrollment.html', semesters=semesters, selected_semester=semester_id, section_stats=section_stats)

@reports_bp.route('/results')
@login_required
@admin_required
def results_report():
    section_id = request.args.get('section_id', type=int)
    sections = CourseSection.query.all()
    grades_list = []
    if section_id:
        enrollments = Enrollment.query.filter_by(section_id=section_id).all()
        enr_ids = [e.id for e in enrollments]
        grades_list = Grade.query.filter(Grade.enrollment_id.in_(enr_ids)).all() if enr_ids else []
    return render_template('reports/results.html', sections=sections, selected_section=section_id, grades=grades_list)

@reports_bp.route('/fees')
@login_required
@admin_required
def fees_report():
    semester_id = request.args.get('semester_id', type=int)
    semesters = Semester.query.all()
    query = StudentInvoice.query
    if semester_id:
        query = query.filter_by(semester_id=semester_id)
    invoices = query.all()
    total_billed = sum([float(i.total_amount) for i in invoices])
    total_collected = sum([float(i.paid_amount) for i in invoices])
    total_pending = max(0.00, total_billed - total_collected)
    return render_template('reports/fees.html', semesters=semesters, selected_semester=semester_id, invoices=invoices, total_billed=total_billed, total_collected=total_collected, total_pending=total_pending)
