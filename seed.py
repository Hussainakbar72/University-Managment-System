import os
from datetime import datetime, date, time
from decimal import Decimal
from app import create_app
from app.extensions import db
from app.models.auth import (
    User, Role, UserRole, Student, Instructor, Staff, Guardian, StudentGuardian
)
from app.models.academic import (
    Campus, Faculty, Department, Program, AcademicYear, Semester, Course, CoursePrerequisite
)
from app.models.enrollment import (
    Classroom, CourseSection, SectionSchedule, Enrollment, Attendance
)
from app.models.examination import (
    Assessment, AssessmentResult, Exam, ExamRoom, ExamSeating, Grade, Transcript
)
from app.models.finance import (
    FeeType, FeeStructure, StudentInvoice, InvoiceItem, Payment, Scholarship, ScholarshipAward
)
from app.models.library import (
    LibraryBook, BookCopy, LibraryLoan, LibraryFine
)
from app.models.hostel import (
    HostelBuilding, HostelRoom, HostelAllocation
)
from app.models.transport import (
    TransportRoute, TransportVehicle, TransportAssignment
)
from app.models.system import (
    Announcement, Notification, AuditLog
)

def seed_database():
    app = create_app()
    with app.app_context():
        print("Cleaning and recreating database with rich university data...")
        db.drop_all()
        db.create_all()

        # ==========================================================
        # 1. ROLES & USERS (Module A)
        # ==========================================================
        roles = {
            'ADMIN': Role(name='ADMIN', description='Full university administrative access'),
            'TEACHER': Role(name='TEACHER', description='Academic instructor & grading permissions'),
            'STUDENT': Role(name='STUDENT', description='Enrolled student portal privileges'),
            'STAFF': Role(name='STAFF', description='Departmental coordinator / clerk')
        }
        for r in roles.values():
            db.session.add(r)
        db.session.flush()

        # Users list
        users_raw = [
            # Admins
            ('admin@ums.edu', 'System', 'Administrator', 'Admin@123', '03001111111', 'ADMIN'),
            # Instructors
            ('dr.tariq@ums.edu', 'Tariq', 'Mahmood', 'Teacher@123', '03002222222', 'TEACHER'),
            ('dr.amna@ums.edu', 'Amna', 'Kashif', 'Teacher@123', '03003333333', 'TEACHER'),
            ('dr.bilal@ums.edu', 'Bilal', 'Ahmed', 'Teacher@123', '03004444444', 'TEACHER'),
            ('dr.sarah@ums.edu', 'Sarah', 'Malik', 'Teacher@123', '03005555555', 'TEACHER'),
            # Staff
            ('staff.kamran@ums.edu', 'Kamran', 'Iqbal', 'Staff@123', '03006666666', 'STAFF'),
            ('staff.sadia@ums.edu', 'Sadia', 'Noreen', 'Staff@123', '03007777777', 'STAFF'),
            # Students
            ('ali.raza@ums.edu', 'Ali', 'Raza', 'Student@123', '03008888888', 'STUDENT'),
            ('fatima.zahra@ums.edu', 'Fatima', 'Zahra', 'Student@123', '03009999999', 'STUDENT'),
            ('usman.khan@ums.edu', 'Usman', 'Khan', 'Student@123', '03001234567', 'STUDENT'),
            ('ayesha.siddiqua@ums.edu', 'Ayesha', 'Siddiqua', 'Student@123', '03002345678', 'STUDENT'),
            ('zain.ulabidin@ums.edu', 'Zain', 'Ul Abidin', 'Student@123', '03003456789', 'STUDENT')
        ]
        u_dict = {}
        for email, fn, ln, pw, ph, r_name in users_raw:
            u = User(email=email, first_name=fn, last_name=ln, phone=ph, is_active=True)
            u.set_password(pw)
            db.session.add(u)
            db.session.flush()
            db.session.add(UserRole(user_id=u.id, role_id=roles[r_name].id))
            u_dict[email] = u
        db.session.flush()

        # ==========================================================
        # 2. CAMPUSES, FACULTIES & DEPARTMENTS (Module B)
        # ==========================================================
        campuses = [
            Campus(name='Islamabad Main Campus', code='ISB-MAIN', address='Sector H-9, Islamabad', city='Islamabad', is_main=True),
            Campus(name='Lahore Executive Campus', code='LHR-EXEC', address='Canal Bank Road, Lahore', city='Lahore', is_main=False),
            Campus(name='Karachi City Campus', code='KHI-CITY', address='Clifton Block 5, Karachi', city='Karachi', is_main=False)
        ]
        db.session.add_all(campuses)
        db.session.flush()

        faculties = [
            Faculty(name='Faculty of Computing & Artificial Intelligence', code='FCAI', campus_id=campuses[0].id, dean_name='Dr. Zahid Mehmood'),
            Faculty(name='Faculty of Engineering & Technology', code='FET', campus_id=campuses[0].id, dean_name='Dr. Salman Khan'),
            Faculty(name='Faculty of Management & Business Studies', code='FMBS', campus_id=campuses[1].id, dean_name='Dr. Naveed Akhtar'),
            Faculty(name='Faculty of Basic & Applied Sciences', code='FBAS', campus_id=campuses[0].id, dean_name='Dr. Rubina Shah'),
            Faculty(name='Faculty of Allied Health Sciences', code='FAHS', campus_id=campuses[0].id, dean_name='Dr. Zahoor Ahmed')
        ]
        db.session.add_all(faculties)
        db.session.flush()

        depts = [
            Department(name='Department of Artificial Intelligence & Data Science', code='AI-DS', faculty_id=faculties[0].id, head_of_department='Dr. Amna Kashif'),
            Department(name='Department of Computer Science', code='CS', faculty_id=faculties[0].id, head_of_department='Dr. Tariq Mahmood'),
            Department(name='Department of Software Engineering', code='SE', faculty_id=faculties[0].id, head_of_department='Dr. Bilal Ahmed'),
            Department(name='Department of Electrical & Computer Engineering', code='EE', faculty_id=faculties[1].id, head_of_department='Dr. Asim Farooq'),
            Department(name='Department of Business Administration', code='BBA', faculty_id=faculties[2].id, head_of_department='Dr. Sarah Malik'),
            Department(name='Department of Accounting & Finance', code='AF', faculty_id=faculties[2].id, head_of_department='Dr. Farhan Qureshi'),
            Department(name='Department of Mathematics & Statistics', code='MATH', faculty_id=faculties[3].id, head_of_department='Dr. Qasim Ali'),
            Department(name='Department of Allied Health Sciences', code='AHS', faculty_id=faculties[4].id, head_of_department='Dr. Noman Tariq')
        ]
        db.session.add_all(depts)
        db.session.flush()

        # ==========================================================
        # 3. PROGRAMS (Module B)
        # ==========================================================
        programs = [
            Program(name='Bachelor of Science in Artificial Intelligence', code='BS-AI', department_id=depts[0].id, degree_type='BS', total_credit_hours=134, duration_years=4),
            Program(name='Bachelor of Science in Data Science', code='BS-DS', department_id=depts[0].id, degree_type='BS', total_credit_hours=132, duration_years=4),
            Program(name='Bachelor of Science in Computer Science', code='BS-CS', department_id=depts[1].id, degree_type='BS', total_credit_hours=130, duration_years=4),
            Program(name='Bachelor of Science in Software Engineering', code='BS-SE', department_id=depts[2].id, degree_type='BS', total_credit_hours=134, duration_years=4),
            Program(name='Bachelor of Business Administration', code='BBA-HONS', department_id=depts[4].id, degree_type='BS', total_credit_hours=128, duration_years=4),
            Program(name='Master of Science in Artificial Intelligence', code='MS-AI', department_id=depts[0].id, degree_type='MS', total_credit_hours=30, duration_years=2),
            Program(name='Bachelor of Science in Medical Laboratory Technology', code='BS-MLT', department_id=depts[7].id, degree_type='BS', total_credit_hours=136, duration_years=4)
        ]
        db.session.add_all(programs)
        db.session.flush()

        # ==========================================================
        # 4. ACADEMIC YEARS & SEMESTERS (Module B)
        # ==========================================================
        ay1 = AcademicYear(year_name='2024-2025', start_date=date(2024, 9, 1), end_date=date(2025, 6, 30), is_current=False)
        ay2 = AcademicYear(year_name='2025-2026', start_date=date(2025, 9, 1), end_date=date(2026, 6, 30), is_current=True)
        db.session.add_all([ay1, ay2])
        db.session.flush()

        semesters = [
            Semester(name='Fall 2024', academic_year_id=ay1.id, start_date=date(2024, 9, 1), end_date=date(2025, 1, 31), is_active=False),
            Semester(name='Spring 2025', academic_year_id=ay1.id, start_date=date(2025, 2, 1), end_date=date(2025, 6, 30), is_active=False),
            Semester(name='Fall 2025', academic_year_id=ay2.id, start_date=date(2025, 9, 1), end_date=date(2026, 1, 31), is_active=True),
            Semester(name='Spring 2026', academic_year_id=ay2.id, start_date=date(2026, 2, 1), end_date=date(2026, 6, 30), is_active=False)
        ]
        db.session.add_all(semesters)
        db.session.flush()

        # ==========================================================
        # 5. COURSES & PREREQUISITES (Module B)
        # ==========================================================
        courses = [
            Course(code='CS-101', title='Programming Fundamentals', credit_hours=4, department_id=depts[1].id, description='C++ and Python structured programming'),
            Course(code='CS-102', title='Object Oriented Programming', credit_hours=4, department_id=depts[1].id, description='OOP paradigms, inheritance, polymorphism'),
            Course(code='CS-201', title='Data Structures & Algorithms', credit_hours=3, department_id=depts[1].id, description='Trees, graphs, dynamic programming'),
            Course(code='AI-101', title='Introduction to Artificial Intelligence', credit_hours=3, department_id=depts[0].id, description='State space search, game playing, agents'),
            Course(code='AI-201', title='Machine Learning & Neural Networks', credit_hours=4, department_id=depts[0].id, description='Supervised, unsupervised learning, deep nets'),
            Course(code='DS-101', title='Introduction to Data Science', credit_hours=3, department_id=depts[0].id, description='EDA, Pandas, NumPy, data wrangling'),
            Course(code='DS-201', title='Big Data Analytics & Mining', credit_hours=3, department_id=depts[0].id, description='Distributed data pipelines, Spark, Hadoop'),
            Course(code='SE-201', title='Web Engineering & Frameworks', credit_hours=3, department_id=depts[2].id, description='Full stack web development using Flask & Bootstrap'),
            Course(code='DBMS-130', title='Database Systems & SQL', credit_hours=4, department_id=depts[1].id, description='Relational model, normalization, transaction processing'),
            Course(code='MTH-101', title='Calculus & Analytical Geometry', credit_hours=3, department_id=depts[6].id, description='Limits, derivatives, multivariable calculus')
        ]
        db.session.add_all(courses)
        db.session.flush()

        # Prerequisites: OOP requires PF, DSA requires OOP, ML requires Intro to AI
        prereqs = [
            CoursePrerequisite(course_id=courses[1].id, prerequisite_id=courses[0].id, minimum_grade='D'),
            CoursePrerequisite(course_id=courses[2].id, prerequisite_id=courses[1].id, minimum_grade='C'),
            CoursePrerequisite(course_id=courses[4].id, prerequisite_id=courses[3].id, minimum_grade='C')
        ]
        db.session.add_all(prereqs)
        db.session.flush()

        # ==========================================================
        # 6. INSTRUCTORS & STAFF (Module A)
        # ==========================================================
        instructors = [
            Instructor(user_id=u_dict['dr.tariq@ums.edu'].id, employee_id='EMP-INS-101', department_id=depts[1].id, designation='Professor', qualification='PhD Computer Science (Cambridge)', joining_date=date(2018, 1, 15)),
            Instructor(user_id=u_dict['dr.amna@ums.edu'].id, employee_id='EMP-INS-102', department_id=depts[0].id, designation='Associate Professor', qualification='PhD Artificial Intelligence (Oxford)', joining_date=date(2019, 8, 1)),
            Instructor(user_id=u_dict['dr.bilal@ums.edu'].id, employee_id='EMP-INS-103', department_id=depts[2].id, designation='Assistant Professor', qualification='PhD Software Engineering (NUST)', joining_date=date(2021, 2, 10)),
            Instructor(user_id=u_dict['dr.sarah@ums.edu'].id, employee_id='EMP-INS-104', department_id=depts[4].id, designation='Lecturer', qualification='MS Management Sciences (LUMS)', joining_date=date(2022, 9, 1))
        ]
        db.session.add_all(instructors)

        staff_list = [
            Staff(user_id=u_dict['staff.kamran@ums.edu'].id, employee_id='EMP-STF-201', department_id=depts[0].id, job_title='Academic Coordinator', hire_date=date(2020, 5, 1)),
            Staff(user_id=u_dict['staff.sadia@ums.edu'].id, employee_id='EMP-STF-202', department_id=depts[1].id, job_title='Examinations Officer', hire_date=date(2021, 7, 15))
        ]
        db.session.add_all(staff_list)
        db.session.flush()

        # ==========================================================
        # 7. STUDENTS & GUARDIANS (Module A)
        # ==========================================================
        students = [
            Student(user_id=u_dict['ali.raza@ums.edu'].id, registration_number='FA24-BAI-001', program_id=programs[0].id, admission_date=date(2024, 9, 1), current_semester=3, status='Active', cgpa=Decimal('3.65')),
            Student(user_id=u_dict['fatima.zahra@ums.edu'].id, registration_number='FA24-BDS-002', program_id=programs[1].id, admission_date=date(2024, 9, 1), current_semester=3, status='Active', cgpa=Decimal('3.88')),
            Student(user_id=u_dict['usman.khan@ums.edu'].id, registration_number='FA24-BCS-003', program_id=programs[2].id, admission_date=date(2024, 9, 1), current_semester=3, status='Active', cgpa=Decimal('3.25')),
            Student(user_id=u_dict['ayesha.siddiqua@ums.edu'].id, registration_number='FA24-BSE-004', program_id=programs[3].id, admission_date=date(2024, 9, 1), current_semester=3, status='Active', cgpa=Decimal('3.75')),
            Student(user_id=u_dict['zain.ulabidin@ums.edu'].id, registration_number='FA24-BBA-005', program_id=programs[4].id, admission_date=date(2024, 9, 1), current_semester=3, status='Active', cgpa=Decimal('3.10'))
        ]
        db.session.add_all(students)
        db.session.flush()

        g1 = Guardian(full_name='Muhammad Raza', relationship='Father', phone='03009988776', email='m.raza@gmail.com', occupation='Civil Engineer', address='House 14, Street 2, F-8/3, Islamabad')
        g2 = Guardian(full_name='Dr. Zahra Bukhari', relationship='Mother', phone='03008877665', email='zahra.bukhari@hospital.org', occupation='Surgeon', address='Plot 45, DHA Phase 2, Islamabad')
        db.session.add_all([g1, g2])
        db.session.flush()

        db.session.add_all([
            StudentGuardian(student_id=students[0].id, guardian_id=g1.id, is_primary=True),
            StudentGuardian(student_id=students[1].id, guardian_id=g2.id, is_primary=True)
        ])
        db.session.flush()

        # ==========================================================
        # 8. CLASSROOMS, SECTIONS, SCHEDULES & ENROLLMENT (Module C)
        # ==========================================================
        classrooms = [
            Classroom(campus_id=campuses[0].id, building_name='Iqbal Block', room_number='Lab 3', capacity=45, room_type='Computer Lab'),
            Classroom(campus_id=campuses[0].id, building_name='Jinnah Block', room_number='Hall A', capacity=120, room_type='Lecture Hall'),
            Classroom(campus_id=campuses[0].id, building_name='Razi Block', room_number='33-309', capacity=60, room_type='Lecture Hall'),
            Classroom(campus_id=campuses[0].id, building_name='Razi Block', room_number='38-719', capacity=55, room_type='Seminar Room')
        ]
        db.session.add_all(classrooms)
        db.session.flush()

        cur_sem = semesters[2] # Fall 2025
        sections = [
            CourseSection(section_name='AI-3A', course_id=courses[3].id, semester_id=cur_sem.id, instructor_id=instructors[1].id, max_capacity=50),
            CourseSection(section_name='DS-3A', course_id=courses[5].id, semester_id=cur_sem.id, instructor_id=instructors[1].id, max_capacity=50),
            CourseSection(section_name='CS-3A', course_id=courses[2].id, semester_id=cur_sem.id, instructor_id=instructors[0].id, max_capacity=60),
            CourseSection(section_name='SE-3A', course_id=courses[7].id, semester_id=cur_sem.id, instructor_id=instructors[2].id, max_capacity=50),
            CourseSection(section_name='DB-3A', course_id=courses[8].id, semester_id=cur_sem.id, instructor_id=instructors[0].id, max_capacity=55)
        ]
        db.session.add_all(sections)
        db.session.flush()

        schedules = [
            SectionSchedule(section_id=sections[0].id, classroom_id=classrooms[0].id, day_of_week='Monday', start_time=time(9, 0), end_time=time(11, 0)),
            SectionSchedule(section_id=sections[1].id, classroom_id=classrooms[2].id, day_of_week='Tuesday', start_time=time(10, 0), end_time=time(12, 0)),
            SectionSchedule(section_id=sections[2].id, classroom_id=classrooms[1].id, day_of_week='Wednesday', start_time=time(11, 0), end_time=time(13, 0)),
            SectionSchedule(section_id=sections[3].id, classroom_id=classrooms[0].id, day_of_week='Thursday', start_time=time(14, 0), end_time=time(16, 0)),
            SectionSchedule(section_id=sections[4].id, classroom_id=classrooms[2].id, day_of_week='Friday', start_time=time(9, 30), end_time=time(11, 30))
        ]
        db.session.add_all(schedules)
        db.session.flush()

        # Enrollments
        enrs = [
            # Ali Raza (Student 0)
            Enrollment(student_id=students[0].id, section_id=sections[0].id, status='Enrolled'),
            Enrollment(student_id=students[0].id, section_id=sections[1].id, status='Enrolled'),
            Enrollment(student_id=students[0].id, section_id=sections[3].id, status='Enrolled'),
            Enrollment(student_id=students[0].id, section_id=sections[4].id, status='Enrolled'),
            # Fatima Zahra (Student 1)
            Enrollment(student_id=students[1].id, section_id=sections[0].id, status='Enrolled'),
            Enrollment(student_id=students[1].id, section_id=sections[1].id, status='Enrolled'),
            Enrollment(student_id=students[1].id, section_id=sections[4].id, status='Enrolled'),
            # Usman Khan (Student 2)
            Enrollment(student_id=students[2].id, section_id=sections[2].id, status='Enrolled'),
            Enrollment(student_id=students[2].id, section_id=sections[4].id, status='Enrolled')
        ]
        db.session.add_all(enrs)
        db.session.flush()

        # Attendance logs
        attendance_logs = [
            Attendance(enrollment_id=enrs[0].id, schedule_id=schedules[0].id, date=date(2025, 9, 8), status='Present', remarks='On time'),
            Attendance(enrollment_id=enrs[0].id, schedule_id=schedules[0].id, date=date(2025, 9, 15), status='Present', remarks='On time'),
            Attendance(enrollment_id=enrs[0].id, schedule_id=schedules[0].id, date=date(2025, 9, 22), status='Present', remarks='On time'),
            Attendance(enrollment_id=enrs[0].id, schedule_id=schedules[0].id, date=date(2025, 9, 29), status='Late', remarks='Late by 5 mins'),
            Attendance(enrollment_id=enrs[1].id, schedule_id=schedules[1].id, date=date(2025, 9, 9), status='Present', remarks='Lab completed'),
            Attendance(enrollment_id=enrs[2].id, schedule_id=schedules[3].id, date=date(2025, 9, 11), status='Present', remarks='Project discussion')
        ]
        db.session.add_all(attendance_logs)
        db.session.flush()

        # ==========================================================
        # 9. ASSESSMENTS, EXAMS & GRADES (Module D)
        # ==========================================================
        assms = [
            Assessment(section_id=sections[0].id, title='Quiz 1 - Heuristic & A* Search', assessment_type='Quiz', max_marks=Decimal('20.00'), weightage=Decimal('5.00'), due_date=date(2025, 9, 25)),
            Assessment(section_id=sections[0].id, title='Assignment 1 - Minimax Agent Implementation', assessment_type='Assignment', max_marks=Decimal('50.00'), weightage=Decimal('10.00'), due_date=date(2025, 10, 10)),
            Assessment(section_id=sections[3].id, title='Project Milestone 1 - Wireframes & DB Schema', assessment_type='Project', max_marks=Decimal('100.00'), weightage=Decimal('15.00'), due_date=date(2025, 10, 15))
        ]
        db.session.add_all(assms)
        db.session.flush()

        db.session.add_all([
            AssessmentResult(assessment_id=assms[0].id, enrollment_id=enrs[0].id, marks_obtained=Decimal('19.00'), feedback='Excellent algorithmic analysis'),
            AssessmentResult(assessment_id=assms[0].id, enrollment_id=enrs[4].id, marks_obtained=Decimal('20.00'), feedback='Perfect score'),
            AssessmentResult(assessment_id=assms[1].id, enrollment_id=enrs[0].id, marks_obtained=Decimal('47.50'), feedback='Well-structured code')
        ])
        db.session.flush()

        exam_ai = Exam(course_id=courses[3].id, semester_id=cur_sem.id, exam_type='Midterm', exam_date=date(2025, 11, 10), start_time=time(10, 0), duration_minutes=120, total_marks=Decimal('50.00'))
        exam_se = Exam(course_id=courses[7].id, semester_id=cur_sem.id, exam_type='Midterm', exam_date=date(2025, 11, 12), start_time=time(14, 0), duration_minutes=120, total_marks=Decimal('50.00'))
        db.session.add_all([exam_ai, exam_se])
        db.session.flush()

        er1 = ExamRoom(exam_id=exam_ai.id, classroom_id=classrooms[1].id, invigilator_name='Dr. Bilal Ahmed')
        db.session.add(er1)
        db.session.flush()

        db.session.add_all([
            ExamSeating(exam_room_id=er1.id, enrollment_id=enrs[0].id, seat_number='DESK-01', is_attended=True),
            ExamSeating(exam_room_id=er1.id, enrollment_id=enrs[4].id, seat_number='DESK-02', is_attended=True)
        ])
        db.session.flush()

        # Final Grades & Transcripts
        db.session.add_all([
            Grade(enrollment_id=enrs[0].id, total_score=Decimal('88.50'), letter_grade='A', grade_points=Decimal('4.00')),
            Grade(enrollment_id=enrs[1].id, total_score=Decimal('82.00'), letter_grade='B+', grade_points=Decimal('3.30')),
            Grade(enrollment_id=enrs[4].id, total_score=Decimal('94.00'), letter_grade='A', grade_points=Decimal('4.00'))
        ])
        db.session.flush()

        tr1 = Transcript(student_id=students[0].id, issue_date=date(2025, 1, 15), total_credits_earned=34, cumulative_gpa=Decimal('3.65'), remarks='Dean Honour Roll')
        tr2 = Transcript(student_id=students[1].id, issue_date=date(2025, 1, 15), total_credits_earned=34, cumulative_gpa=Decimal('3.88'), remarks='Gold Medalist Track')
        db.session.add_all([tr1, tr2])
        db.session.flush()

        # ==========================================================
        # 10. FINANCE & FEES (Module E)
        # ==========================================================
        fee_types = [
            FeeType(name='Tuition Fee', description='Course teaching & academic instruction fee'),
            FeeType(name='Computing & AI Lab Fee', description='High performance GPU & cloud access charges'),
            FeeType(name='Library & Journal Subscription', description='IEEE / ACM digital library access'),
            FeeType(name='Hostel Accomodation Fee', description='Semester room lodging & utilities'),
            FeeType(name='Campus Transport Pass', description='Semester shuttle service pass')
        ]
        db.session.add_all(fee_types)
        db.session.flush()

        fee_structures = [
            FeeStructure(fee_type_id=fee_types[0].id, program_id=programs[0].id, semester_id=cur_sem.id, amount=Decimal('85000.00')),
            FeeStructure(fee_type_id=fee_types[1].id, program_id=programs[0].id, semester_id=cur_sem.id, amount=Decimal('10000.00')),
            FeeStructure(fee_type_id=fee_types[0].id, program_id=programs[1].id, semester_id=cur_sem.id, amount=Decimal('80000.00')),
            FeeStructure(fee_type_id=fee_types[0].id, program_id=programs[2].id, semester_id=cur_sem.id, amount=Decimal('78000.00'))
        ]
        db.session.add_all(fee_structures)
        db.session.flush()

        inv1 = StudentInvoice(invoice_number='INV-2025-001', student_id=students[0].id, semester_id=cur_sem.id, total_amount=Decimal('95000.00'), paid_amount=Decimal('95000.00'), issue_date=date(2025, 8, 15), due_date=date(2025, 9, 10), status='Paid')
        inv2 = StudentInvoice(invoice_number='INV-2025-002', student_id=students[1].id, semester_id=cur_sem.id, total_amount=Decimal('80000.00'), paid_amount=Decimal('40000.00'), issue_date=date(2025, 8, 15), due_date=date(2025, 9, 10), status='Partially Paid')
        inv3 = StudentInvoice(invoice_number='INV-2025-003', student_id=students[2].id, semester_id=cur_sem.id, total_amount=Decimal('78000.00'), paid_amount=Decimal('0.00'), issue_date=date(2025, 8, 15), due_date=date(2025, 9, 10), status='Unpaid')
        db.session.add_all([inv1, inv2, inv3])
        db.session.flush()

        db.session.add_all([
            InvoiceItem(invoice_id=inv1.id, fee_type_id=fee_types[0].id, description='Fall 2025 Tuition Fee', amount=Decimal('85000.00')),
            InvoiceItem(invoice_id=inv1.id, fee_type_id=fee_types[1].id, description='AI & Cloud Lab Computing', amount=Decimal('10000.00')),
            InvoiceItem(invoice_id=inv2.id, fee_type_id=fee_types[0].id, description='Fall 2025 Tuition Fee', amount=Decimal('80000.00'))
        ])
        db.session.flush()

        db.session.add_all([
            Payment(transaction_id='TXN-HBL-998811', invoice_id=inv1.id, amount=Decimal('95000.00'), payment_method='Bank Transfer', status='Completed'),
            Payment(transaction_id='TXN-CARD-442200', invoice_id=inv2.id, amount=Decimal('40000.00'), payment_method='Credit Card', status='Completed')
        ])
        db.session.flush()

        sc1 = Scholarship(name='Vice Chancellor Merit Scholarship', description='Awarded for CGPA > 3.8', discount_percentage=Decimal('50.00'), eligibility_criteria='Maintain minimum CGPA 3.8')
        sc2 = Scholarship(name='Need-Based Higher Education Grant', description='Financial assistance program', discount_percentage=Decimal('25.00'), eligibility_criteria='Income verification')
        db.session.add_all([sc1, sc2])
        db.session.flush()

        db.session.add(ScholarshipAward(scholarship_id=sc1.id, student_id=students[1].id, awarded_date=date(2025, 9, 1), status='Active'))
        db.session.flush()

        # ==========================================================
        # 11. LIBRARY, HOSTEL & TRANSPORT (Modules F, G, H)
        # ==========================================================
        books = [
            LibraryBook(isbn='978-0134610993', title='Artificial Intelligence: A Modern Approach', author='Stuart Russell, Peter Norvig', publisher='Pearson', publication_year=2020, category='Artificial Intelligence'),
            LibraryBook(isbn='978-1491957660', title='Python for Data Analysis', author='Wes McKinney', publisher='O Reilly', publication_year=2022, category='Data Science'),
            LibraryBook(isbn='978-0262033848', title='Introduction to Algorithms (CLRS)', author='Thomas H. Cormen', publisher='MIT Press', publication_year=2022, category='Algorithms'),
            LibraryBook(isbn='978-0133970777', title='Database System Concepts', author='Silberschatz, Korth', publisher='McGraw-Hill', publication_year=2020, category='Databases')
        ]
        db.session.add_all(books)
        db.session.flush()

        copies = [
            BookCopy(book_id=books[0].id, barcode='BC-AI-001', status='Borrowed', shelf_location='Shelf A-3'),
            BookCopy(book_id=books[0].id, barcode='BC-AI-002', status='Available', shelf_location='Shelf A-3'),
            BookCopy(book_id=books[1].id, barcode='BC-DS-101', status='Available', shelf_location='Shelf B-2'),
            BookCopy(book_id=books[2].id, barcode='BC-CS-201', status='Available', shelf_location='Shelf C-1')
        ]
        db.session.add_all(copies)
        db.session.flush()

        loan = LibraryLoan(book_copy_id=copies[0].id, user_id=u_dict['ali.raza@ums.edu'].id, borrow_date=date(2025, 9, 15), due_date=date(2025, 9, 29), status='Active')
        db.session.add(loan)
        db.session.flush()

        fine = LibraryFine(loan_id=loan.id, amount=Decimal('5.00'), status='Unpaid')
        db.session.add(fine)

        # Hostel
        hb = HostelBuilding(name='Iqbal Boys Hall', campus_id=campuses[0].id, gender_type='Male', warden_name='Malik Arshad', total_floors=4)
        db.session.add(hb)
        db.session.flush()

        hr = HostelRoom(building_id=hb.id, room_number='Room 204', capacity=2, monthly_fee=Decimal('12000.00'), room_type='Standard')
        db.session.add(hr)
        db.session.flush()

        ha = HostelAllocation(room_id=hr.id, student_id=students[0].id, allocated_date=date(2025, 9, 1), status='Active')
        db.session.add(ha)

        # Transport
        routes = [
            TransportRoute(route_name='Route 01 - Rawalpindi Saddar to Campus', start_point='Saddar Metro Station', end_point='Main Islamabad Campus', stops_description='Saddar, Committee Chowk, Faizabad, I-8, H-9 Campus', monthly_fare=Decimal('6000.00')),
            TransportRoute(route_name='Route 02 - Islamabad DHA to Campus', start_point='DHA Phase 2 Gate 1', end_point='Main Islamabad Campus', stops_description='DHA 2, Bahria Town, Rawat, Expressway, H-9', monthly_fare=Decimal('7000.00'))
        ]
        db.session.add_all(routes)
        db.session.flush()

        veh = TransportVehicle(vehicle_number='ICT-BUS-88', route_id=routes[0].id, capacity=52, driver_name='Muhammad Akram', driver_phone='03125554433', status='Active')
        db.session.add(veh)
        db.session.flush()

        ta = TransportAssignment(vehicle_id=veh.id, user_id=u_dict['ali.raza@ums.edu'].id, pickup_stop='Faizabad Interchange', assigned_date=date(2025, 9, 1), status='Active')
        db.session.add(ta)

        # ==========================================================
        # 12. SYSTEM, NOTIFICATIONS & AUDIT (Module I)
        # ==========================================================
        announcements = [
            Announcement(title='Welcome to Fall 2025 Semester', content='Orientation ceremony and commencement of regular classes will begin on Monday. Check your timetables.', target_audience='All', author_id=u_dict['admin@ums.edu'].id, is_published=True),
            Announcement(title='Summer Training & AI Internship with Live Projects', content='Applications are open for 3rd semester students in collaboration with tech partners.', target_audience='Students', author_id=u_dict['admin@ums.edu'].id, is_published=True),
            Announcement(title='Mid Term Examination Timetable Published', content='Please review your assigned exam halls and desk allocations on your student portals.', target_audience='Students', author_id=u_dict['admin@ums.edu'].id, is_published=True)
        ]
        db.session.add_all(announcements)
        db.session.flush()

        notifs = [
            Notification(user_id=u_dict['ali.raza@ums.edu'].id, title='Fee Invoice Paid in Full', message='Invoice INV-2025-001 has been confirmed paid via Bank Transfer.', is_read=False),
            Notification(user_id=u_dict['fatima.zahra@ums.edu'].id, title='Scholarship Award Confirmed', message='Congratulations! 50% VC Merit Scholarship has been awarded to your account.', is_read=True)
        ]
        db.session.add_all(notifs)

        audit = AuditLog(user_id=u_dict['admin@ums.edu'].id, action='RICH_UNIVERSITY_INITIALIZATION', table_name='ALL_48_TABLES', record_id=1, ip_address='127.0.0.1', details='Full university relational hierarchy populated across 3 Campuses, 4 Faculties, 7 Departments, 6 Programs, 10 Courses, Classrooms, Sections, Invoices, Library, Hostel and Transport.')
        db.session.add(audit)

        db.session.commit()
        print("SUCCESS: Rich multi-campus university network successfully generated and verified across all 48 tables!")

if __name__ == '__main__':
    seed_database()
