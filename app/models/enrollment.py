from datetime import datetime
from app.extensions import db

class Classroom(db.Model):
    __tablename__ = 'classrooms'

    id = db.Column(db.Integer, primary_key=True)
    room_number = db.Column(db.String(50), nullable=False, index=True)
    building_name = db.Column(db.String(100), nullable=False)
    campus_id = db.Column(db.Integer, db.ForeignKey('campuses.id', ondelete='CASCADE'), nullable=False, index=True)
    capacity = db.Column(db.Integer, nullable=False)
    room_type = db.Column(db.String(50), default='Lecture Hall', nullable=False)  # Lab, Seminar, Lecture Hall

    campus = db.relationship('Campus', back_populates='classrooms')
    schedules = db.relationship('SectionSchedule', back_populates='classroom')
    exam_rooms = db.relationship('ExamRoom', back_populates='classroom')

    __table_args__ = (
        db.UniqueConstraint('campus_id', 'building_name', 'room_number', name='uq_campus_classroom'),
    )

    def __repr__(self):
        return f"<Classroom {self.building_name} - {self.room_number}>"


class CourseSection(db.Model):
    __tablename__ = 'course_sections'

    id = db.Column(db.Integer, primary_key=True)
    section_name = db.Column(db.String(20), nullable=False)  # A, B, CS-1A
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False, index=True)
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id', ondelete='CASCADE'), nullable=False, index=True)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructors.id', ondelete='SET NULL'), nullable=True, index=True)
    max_capacity = db.Column(db.Integer, default=50, nullable=False)

    course = db.relationship('Course', back_populates='sections')
    semester = db.relationship('Semester', back_populates='sections')
    instructor = db.relationship('Instructor', back_populates='sections')

    schedules = db.relationship('SectionSchedule', back_populates='section', cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', back_populates='section', cascade='all, delete-orphan')
    assessments = db.relationship('Assessment', back_populates='section', cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('course_id', 'semester_id', 'section_name', name='uq_course_semester_section'),
    )

    def __repr__(self):
        return f"<Section {self.section_name} ({self.course.code if self.course else self.course_id})>"


class SectionSchedule(db.Model):
    __tablename__ = 'section_schedules'

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('course_sections.id', ondelete='CASCADE'), nullable=False, index=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id', ondelete='SET NULL'), nullable=True, index=True)
    day_of_week = db.Column(db.String(20), nullable=False)  # Monday, Tuesday, etc.
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    section = db.relationship('CourseSection', back_populates='schedules')
    classroom = db.relationship('Classroom', back_populates='schedules')
    attendances = db.relationship('Attendance', back_populates='schedule')

    @property
    def schedule_section(self):
        return f"{self.section.course.code if self.section and self.section.course else ''} - Sec {self.section.section_name if self.section else self.section_id}"

    @property
    def classroom_display(self):
        return f"{self.classroom.building_name} ({self.classroom.room_number})" if self.classroom else 'Unassigned'

    def __repr__(self):
        return f"<Schedule Section:{self.section_id} {self.day_of_week} {self.start_time}-{self.end_time}>"


class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    section_id = db.Column(db.Integer, db.ForeignKey('course_sections.id', ondelete='CASCADE'), nullable=False, index=True)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), default='Enrolled', nullable=False)  # Enrolled, Dropped, Withdrawn, Completed

    student = db.relationship('Student', back_populates='enrollments')
    section = db.relationship('CourseSection', back_populates='enrollments')

    attendance_records = db.relationship('Attendance', back_populates='enrollment', cascade='all, delete-orphan')
    assessment_results = db.relationship('AssessmentResult', back_populates='enrollment', cascade='all, delete-orphan')
    exam_seatings = db.relationship('ExamSeating', back_populates='enrollment', cascade='all, delete-orphan')
    grade = db.relationship('Grade', back_populates='enrollment', uselist=False, cascade='all, delete-orphan')

    @property
    def student_reg_number(self):
        return self.student.registration_number if self.student else f"Student #{self.student_id}"

    @property
    def course_name(self):
        return f"{self.section.course.code} - {self.section.course.title}" if self.section and self.section.course else "N/A"

    @property
    def section_title(self):
        return f"Section {self.section.section_name}" if self.section else f"Section #{self.section_id}"

    __table_args__ = (
        db.UniqueConstraint('student_id', 'section_id', name='uq_student_section_enrollment'),
    )

    def __repr__(self):
        return f"<Enrollment Student:{self.student_id} Section:{self.section_id}>"


class Attendance(db.Model):
    __tablename__ = 'attendance'

    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.id', ondelete='CASCADE'), nullable=False, index=True)
    schedule_id = db.Column(db.Integer, db.ForeignKey('section_schedules.id', ondelete='SET NULL'), nullable=True, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False)  # Present, Absent, Late, Excused
    remarks = db.Column(db.String(255), nullable=True)

    enrollment = db.relationship('Enrollment', back_populates='attendance_records')
    schedule = db.relationship('SectionSchedule', back_populates='attendances')

    @property
    def student_reg(self):
        return self.enrollment.student.registration_number if self.enrollment and self.enrollment.student else f"#{self.enrollment_id}"

    @property
    def course_code(self):
        return self.enrollment.section.course.code if self.enrollment and self.enrollment.section and self.enrollment.section.course else "N/A"

    __table_args__ = (
        db.UniqueConstraint('enrollment_id', 'date', name='uq_enrollment_date_attendance'),
    )

    def __repr__(self):
        return f"<Attendance Enrollment:{self.enrollment_id} Date:{self.date} Status:{self.status}>"
