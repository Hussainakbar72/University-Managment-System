from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.extensions import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    roles = db.relationship('UserRole', back_populates='user', cascade='all, delete-orphan')
    student_profile = db.relationship('Student', back_populates='user', uselist=False, cascade='all, delete-orphan')
    instructor_profile = db.relationship('Instructor', back_populates='user', uselist=False, cascade='all, delete-orphan')
    staff_profile = db.relationship('Staff', back_populates='user', uselist=False, cascade='all, delete-orphan')
    announcements = db.relationship('Announcement', back_populates='author')
    notifications = db.relationship('Notification', back_populates='user', cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', back_populates='user')
    library_loans = db.relationship('LibraryLoan', back_populates='user')
    transport_assignments = db.relationship('TransportAssignment', back_populates='user')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def has_role(self, role_name):
        return any(ur.role.name.upper() == role_name.upper() for ur in self.roles if ur.role)

    def get_role_names(self):
        return [ur.role.name for ur in self.roles if ur.role]

    def __repr__(self):
        return f"<User {self.email} ({self.full_name})>"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Role(db.Model):
    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.String(255), nullable=True)

    users = db.relationship('UserRole', back_populates='role', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Role {self.name}>"


class UserRole(db.Model):
    __tablename__ = 'user_roles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id', ondelete='CASCADE'), nullable=False, index=True)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', back_populates='roles')
    role = db.relationship('Role', back_populates='users')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
    )

    def __repr__(self):
        return f"<UserRole User:{self.user_id} Role:{self.role_id}>"


class Student(db.Model):
    __tablename__ = 'students'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    registration_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id', ondelete='SET NULL'), nullable=True, index=True)
    admission_date = db.Column(db.Date, nullable=False)
    current_semester = db.Column(db.Integer, default=1, nullable=False)
    status = db.Column(db.String(20), default='Active', nullable=False)  # Active, Suspended, Graduated, Inactive
    cgpa = db.Column(db.Numeric(3, 2), default=0.00, nullable=False)

    user = db.relationship('User', back_populates='student_profile')
    program = db.relationship('Program', back_populates='students')
    guardians = db.relationship('StudentGuardian', back_populates='student', cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', back_populates='student', cascade='all, delete-orphan')
    transcripts = db.relationship('Transcript', back_populates='student', cascade='all, delete-orphan')
    invoices = db.relationship('StudentInvoice', back_populates='student', cascade='all, delete-orphan')
    scholarship_awards = db.relationship('ScholarshipAward', back_populates='student', cascade='all, delete-orphan')
    hostel_allocations = db.relationship('HostelAllocation', back_populates='student', cascade='all, delete-orphan')

    @property
    def student_name(self):
        return self.user.full_name if self.user else 'N/A'

    @property
    def program_code(self):
        return self.program.code if self.program else 'N/A'

    def __repr__(self):
        return f"<Student {self.registration_number}>"


class Instructor(db.Model):
    __tablename__ = 'instructors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    employee_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True, index=True)
    designation = db.Column(db.String(80), nullable=False)  # Professor, Associate Prof, Assistant Prof, Lecturer
    qualification = db.Column(db.String(120), nullable=True)
    joining_date = db.Column(db.Date, nullable=False)

    user = db.relationship('User', back_populates='instructor_profile')
    department = db.relationship('Department', back_populates='instructors')
    sections = db.relationship('CourseSection', back_populates='instructor')

    @property
    def name(self):
        return self.user.full_name if self.user else 'N/A'

    @property
    def department_name(self):
        return self.department.name if self.department else 'N/A'

    def __repr__(self):
        return f"<Instructor {self.employee_id}>"


class Staff(db.Model):
    __tablename__ = 'staff'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=False)
    employee_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True, index=True)
    job_title = db.Column(db.String(100), nullable=False)
    hire_date = db.Column(db.Date, nullable=False)

    user = db.relationship('User', back_populates='staff_profile')
    department = db.relationship('Department', back_populates='staff_members')

    def __repr__(self):
        return f"<Staff {self.employee_id} ({self.job_title})>"


class Guardian(db.Model):
    __tablename__ = 'guardians'

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    relationship = db.Column(db.String(50), nullable=False)  # Father, Mother, Guardian, etc.
    phone = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    address = db.Column(db.Text, nullable=True)

    students = db.relationship('StudentGuardian', back_populates='guardian', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Guardian {self.full_name}>"


class StudentGuardian(db.Model):
    __tablename__ = 'student_guardians'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    guardian_id = db.Column(db.Integer, db.ForeignKey('guardians.id', ondelete='CASCADE'), nullable=False, index=True)
    is_primary = db.Column(db.Boolean, default=False, nullable=False)

    student = db.relationship('Student', back_populates='guardians')
    guardian = db.relationship('Guardian', back_populates='students')

    __table_args__ = (
        db.UniqueConstraint('student_id', 'guardian_id', name='uq_student_guardian'),
    )

    def __repr__(self):
        return f"<StudentGuardian Student:{self.student_id} Guardian:{self.guardian_id}>"
