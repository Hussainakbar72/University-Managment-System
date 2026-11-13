from datetime import datetime
from app.extensions import db

class Campus(db.Model):
    __tablename__ = 'campuses'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(60), nullable=False)
    is_main = db.Column(db.Boolean, default=False, nullable=False)

    faculties = db.relationship('Faculty', back_populates='campus', cascade='all, delete-orphan')
    classrooms = db.relationship('Classroom', back_populates='campus', cascade='all, delete-orphan')
    hostel_buildings = db.relationship('HostelBuilding', back_populates='campus', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Campus {self.name} ({self.code})>"


class Faculty(db.Model):
    __tablename__ = 'faculties'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    campus_id = db.Column(db.Integer, db.ForeignKey('campuses.id', ondelete='CASCADE'), nullable=False, index=True)
    dean_name = db.Column(db.String(120), nullable=True)

    campus = db.relationship('Campus', back_populates='faculties')
    departments = db.relationship('Department', back_populates='faculty', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Faculty {self.name}>"


class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False, index=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    faculty_id = db.Column(db.Integer, db.ForeignKey('faculties.id', ondelete='CASCADE'), nullable=False, index=True)
    head_of_department = db.Column(db.String(120), nullable=True)

    faculty = db.relationship('Faculty', back_populates='departments')
    programs = db.relationship('Program', back_populates='department', cascade='all, delete-orphan')
    courses = db.relationship('Course', back_populates='department', cascade='all, delete-orphan')
    instructors = db.relationship('Instructor', back_populates='department')
    staff_members = db.relationship('Staff', back_populates='department')

    def __repr__(self):
        return f"<Department {self.name}>"


class Program(db.Model):
    __tablename__ = 'programs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, index=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), nullable=False, index=True)
    degree_type = db.Column(db.String(50), nullable=False)  # BS, MS, PhD
    total_credit_hours = db.Column(db.Integer, nullable=False)
    duration_years = db.Column(db.Integer, default=4, nullable=False)

    department = db.relationship('Department', back_populates='programs')
    students = db.relationship('Student', back_populates='program')
    fee_structures = db.relationship('FeeStructure', back_populates='program')

    def __repr__(self):
        return f"<Program {self.code} - {self.name}>"


class AcademicYear(db.Model):
    __tablename__ = 'academic_years'

    id = db.Column(db.Integer, primary_key=True)
    year_name = db.Column(db.String(50), unique=True, nullable=False)  # e.g., 2025-2026
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_current = db.Column(db.Boolean, default=False, nullable=False)

    semesters = db.relationship('Semester', back_populates='academic_year', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<AcademicYear {self.year_name}>"


class Semester(db.Model):
    __tablename__ = 'semesters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)  # Fall 2025, Spring 2026, Summer 2026
    academic_year_id = db.Column(db.Integer, db.ForeignKey('academic_years.id', ondelete='CASCADE'), nullable=False, index=True)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=False, nullable=False)

    academic_year = db.relationship('AcademicYear', back_populates='semesters')
    sections = db.relationship('CourseSection', back_populates='semester', cascade='all, delete-orphan')
    exams = db.relationship('Exam', back_populates='semester', cascade='all, delete-orphan')
    fee_structures = db.relationship('FeeStructure', back_populates='semester')
    student_invoices = db.relationship('StudentInvoice', back_populates='semester')

    def __repr__(self):
        return f"<Semester {self.name}>"


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    credit_hours = db.Column(db.Integer, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='CASCADE'), nullable=False, index=True)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id', ondelete='SET NULL'), nullable=True, index=True)
    description = db.Column(db.Text, nullable=True)

    department = db.relationship('Department', back_populates='courses')
    program = db.relationship('Program', backref='program_courses')
    sections = db.relationship('CourseSection', back_populates='course', cascade='all, delete-orphan')
    exams = db.relationship('Exam', back_populates='course', cascade='all, delete-orphan')

    @property
    def department_name(self):
        return self.department.name if self.department else 'N/A'

    @property
    def program_name(self):
        if self.program:
            return self.program.code
        elif self.department and self.department.programs:
            return self.department.programs[0].code
        return 'General'

    prerequisites = db.relationship(
        'CoursePrerequisite',
        foreign_keys='CoursePrerequisite.course_id',
        back_populates='course',
        cascade='all, delete-orphan'
    )
    is_prerequisite_for = db.relationship(
        'CoursePrerequisite',
        foreign_keys='CoursePrerequisite.prerequisite_id',
        back_populates='prerequisite_course',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f"<Course {self.code} - {self.title}>"


class CoursePrerequisite(db.Model):
    __tablename__ = 'course_prerequisites'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False, index=True)
    prerequisite_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False, index=True)
    minimum_grade = db.Column(db.String(5), default='D', nullable=False)

    course = db.relationship('Course', foreign_keys=[course_id], back_populates='prerequisites')
    prerequisite_course = db.relationship('Course', foreign_keys=[prerequisite_id], back_populates='is_prerequisite_for')

    @property
    def course_display(self):
        return f"{self.course.code} - {self.course.title}" if self.course else f"Course #{self.course_id}"

    @property
    def prerequisite_display(self):
        return f"{self.prerequisite_course.code} - {self.prerequisite_course.title}" if self.prerequisite_course else f"Course #{self.prerequisite_id}"

    __table_args__ = (
        db.UniqueConstraint('course_id', 'prerequisite_id', name='uq_course_prereq'),
    )

    def __repr__(self):
        return f"<Prerequisite Course:{self.course_id} Requires:{self.prerequisite_id}>"
