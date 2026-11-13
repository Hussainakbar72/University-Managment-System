from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import func
from app.extensions import db
from app.models.auth import User, Student, Instructor, Role
from app.models.academic import Department, Course, Semester
from app.models.enrollment import CourseSection, Enrollment, Attendance, SectionSchedule
from app.models.examination import Grade, Assessment
from app.models.finance import StudentInvoice, Payment
from app.models.system import Announcement, AuditLog

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return redirect(url_for('auth.login'))

@dashboard_bp.route('/dashboard')
@login_required
def index():
    user_roles = [r.name.upper() for r in [ur.role for ur in current_user.roles if ur.role]]
    
    # --- ADMIN DASHBOARD ---
    if 'ADMIN' in user_roles:
        total_students = db.session.query(func.count(Student.id)).scalar() or 0
        total_instructors = db.session.query(func.count(Instructor.id)).scalar() or 0
        total_departments = db.session.query(func.count(Department.id)).scalar() or 0
        total_courses = db.session.query(func.count(Course.id)).scalar() or 0
        total_revenue = db.session.query(func.sum(Payment.amount)).filter(Payment.status == 'Completed').scalar() or 0.00
        total_invoiced = db.session.query(func.sum(StudentInvoice.total_amount)).scalar() or 0.00
        pending_fees = max(0.00, float(total_invoiced) - float(total_revenue))
        
        recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(8).all()
        recent_students = Student.query.order_by(Student.id.desc()).limit(5).all()
        announcements = Announcement.query.filter_by(is_published=True).order_by(Announcement.created_at.desc()).limit(5).all()

        return render_template(
            'dashboards/admin.html',
            total_students=total_students,
            total_instructors=total_instructors,
            total_departments=total_departments,
            total_courses=total_courses,
            total_revenue=float(total_revenue),
            pending_fees=float(pending_fees),
            recent_logs=recent_logs,
            recent_students=recent_students,
            announcements=announcements
        )

    # --- TEACHER DASHBOARD ---
    elif 'TEACHER' in user_roles:
        instructor = current_user.instructor_profile
        assigned_sections = []
        total_students_taught = 0
        today_schedules = []
        recent_assessments = []

        if instructor:
            assigned_sections = CourseSection.query.filter_by(instructor_id=instructor.id).all()
            section_ids = [s.id for s in assigned_sections]
            if section_ids:
                total_students_taught = db.session.query(func.count(Enrollment.id)).filter(
                    Enrollment.section_id.in_(section_ids),
                    Enrollment.status == 'Enrolled'
                ).scalar() or 0
                today_schedules = SectionSchedule.query.filter(SectionSchedule.section_id.in_(section_ids)).all()
                recent_assessments = Assessment.query.filter(Assessment.section_id.in_(section_ids)).order_by(Assessment.id.desc()).limit(5).all()

        return render_template(
            'dashboards/teacher.html',
            instructor=instructor,
            assigned_sections=assigned_sections,
            total_students_taught=total_students_taught,
            today_schedules=today_schedules,
            recent_assessments=recent_assessments
        )

    # --- STAFF DASHBOARD (Issue #5) ---
    elif 'STAFF' in user_roles:
        from app.models.library import LibraryBook, LibraryLoan
        from app.models.hostel import HostelRoom
        from app.models.transport import TransportRoute

        staff_profile = current_user.staff_profile
        total_books = db.session.query(func.count(LibraryBook.id)).scalar() or 0
        active_loans = db.session.query(func.count(LibraryLoan.id)).filter(LibraryLoan.status == 'Issued').scalar() or 0
        total_hostel_rooms = db.session.query(func.count(HostelRoom.id)).scalar() or 0
        total_routes = db.session.query(func.count(TransportRoute.id)).scalar() or 0
        announcements = Announcement.query.filter_by(is_published=True).order_by(Announcement.created_at.desc()).limit(5).all()

        return render_template(
            'dashboards/staff.html',
            staff=staff_profile,
            total_books=total_books,
            active_loans=active_loans,
            total_hostel_rooms=total_hostel_rooms,
            total_routes=total_routes,
            announcements=announcements
        )

    # --- STUDENT DASHBOARD (Issue #6) ---
    else:
        student = current_user.student_profile
        enrollments = []
        student_schedules = []
        student_cgpa = None
        attendance_percentage = 0.0
        recent_grades = []
        invoices = []
        pending_fees = 0.0
        announcements = Announcement.query.filter(
            Announcement.is_published == True,
            Announcement.target_audience.in_(['All', 'Students'])
        ).order_by(Announcement.created_at.desc()).limit(5).all()

        if student:
            enrollments = Enrollment.query.filter_by(student_id=student.id).all()
            enrollment_ids = [e.id for e in enrollments]
            section_ids = [e.section_id for e in enrollments if e.section_id]
            
            if section_ids:
                student_schedules = SectionSchedule.query.filter(SectionSchedule.section_id.in_(section_ids)).all()

            if enrollment_ids:
                total_classes = db.session.query(func.count(Attendance.id)).filter(Attendance.enrollment_id.in_(enrollment_ids)).scalar() or 0
                present_classes = db.session.query(func.count(Attendance.id)).filter(
                    Attendance.enrollment_id.in_(enrollment_ids),
                    Attendance.status.in_(['Present', 'Late'])
                ).scalar() or 0
                if total_classes > 0:
                    attendance_percentage = round((present_classes / total_classes) * 100, 1)

                recent_grades = Grade.query.filter(Grade.enrollment_id.in_(enrollment_ids)).all()
                grade_pts = [float(g.grade_points) for g in recent_grades if g.grade_points is not None]
                if grade_pts:
                    student_cgpa = round(sum(grade_pts) / len(grade_pts), 2)

            invoices = StudentInvoice.query.filter_by(student_id=student.id).order_by(StudentInvoice.issue_date.desc()).all()
            total_inv = sum([float(inv.total_amount) for inv in invoices])
            total_paid = sum([float(inv.paid_amount) for inv in invoices])
            pending_fees = max(0.00, total_inv - total_paid)

        return render_template(
            'dashboards/student.html',
            student=student,
            enrollments=enrollments,
            student_schedules=student_schedules,
            student_cgpa=student_cgpa,
            attendance_percentage=attendance_percentage,
            recent_grades=recent_grades,
            invoices=invoices,
            pending_fees=pending_fees,
            announcements=announcements
        )

