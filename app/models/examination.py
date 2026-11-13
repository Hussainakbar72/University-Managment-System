from datetime import datetime
from app.extensions import db

class Assessment(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('course_sections.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)  # Quiz 1, Assignment 2, Midterm Project
    assessment_type = db.Column(db.String(50), nullable=False)  # Quiz, Assignment, Project, Lab
    max_marks = db.Column(db.Numeric(5, 2), nullable=False)
    weightage = db.Column(db.Numeric(5, 2), nullable=False)  # e.g., 10%
    due_date = db.Column(db.Date, nullable=False)

    section = db.relationship('CourseSection', back_populates='assessments')
    results = db.relationship('AssessmentResult', back_populates='assessment', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Assessment {self.title} (Section {self.section_id})>"


class AssessmentResult(db.Model):
    __tablename__ = 'assessment_results'

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False, index=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.id', ondelete='CASCADE'), nullable=False, index=True)
    marks_obtained = db.Column(db.Numeric(5, 2), nullable=False)
    feedback = db.Column(db.Text, nullable=True)
    graded_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    assessment = db.relationship('Assessment', back_populates='results')
    enrollment = db.relationship('Enrollment', back_populates='assessment_results')

    __table_args__ = (
        db.UniqueConstraint('assessment_id', 'enrollment_id', name='uq_assessment_enrollment'),
    )

    def __repr__(self):
        return f"<AssessmentResult Assessment:{self.assessment_id} Enrollment:{self.enrollment_id}>"


class Exam(db.Model):
    __tablename__ = 'exams'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id', ondelete='CASCADE'), nullable=False, index=True)
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id', ondelete='CASCADE'), nullable=False, index=True)
    exam_type = db.Column(db.String(50), nullable=False)  # Midterm, Final, Supplementary
    exam_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    duration_minutes = db.Column(db.Integer, default=180, nullable=False)
    total_marks = db.Column(db.Numeric(5, 2), default=100.00, nullable=False)

    course = db.relationship('Course', back_populates='exams')
    semester = db.relationship('Semester', back_populates='exams')
    exam_rooms = db.relationship('ExamRoom', back_populates='exam', cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('course_id', 'semester_id', 'exam_type', name='uq_course_semester_exam'),
    )

    def __repr__(self):
        return f"<Exam {self.exam_type} - {self.course.code if self.course else self.course_id}>"


class ExamRoom(db.Model):
    __tablename__ = 'exam_rooms'

    id = db.Column(db.Integer, primary_key=True)
    exam_id = db.Column(db.Integer, db.ForeignKey('exams.id', ondelete='CASCADE'), nullable=False, index=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classrooms.id', ondelete='CASCADE'), nullable=False, index=True)
    invigilator_name = db.Column(db.String(120), nullable=True)

    exam = db.relationship('Exam', back_populates='exam_rooms')
    classroom = db.relationship('Classroom', back_populates='exam_rooms')
    seatings = db.relationship('ExamSeating', back_populates='exam_room', cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('exam_id', 'classroom_id', name='uq_exam_classroom'),
    )

    def __repr__(self):
        return f"<ExamRoom Exam:{self.exam_id} Room:{self.classroom_id}>"


class ExamSeating(db.Model):
    __tablename__ = 'exam_seating'

    id = db.Column(db.Integer, primary_key=True)
    exam_room_id = db.Column(db.Integer, db.ForeignKey('exam_rooms.id', ondelete='CASCADE'), nullable=False, index=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.id', ondelete='CASCADE'), nullable=False, index=True)
    seat_number = db.Column(db.String(30), nullable=False)
    is_attended = db.Column(db.Boolean, default=True, nullable=False)

    exam_room = db.relationship('ExamRoom', back_populates='seatings')
    enrollment = db.relationship('Enrollment', back_populates='exam_seatings')

    __table_args__ = (
        db.UniqueConstraint('exam_room_id', 'seat_number', name='uq_room_seat'),
        db.UniqueConstraint('exam_room_id', 'enrollment_id', name='uq_room_enrollment_seating'),
    )

    def __repr__(self):
        return f"<ExamSeating Seat:{self.seat_number} Enrollment:{self.enrollment_id}>"


class Grade(db.Model):
    __tablename__ = 'grades'

    id = db.Column(db.Integer, primary_key=True)
    enrollment_id = db.Column(db.Integer, db.ForeignKey('enrollments.id', ondelete='CASCADE'), unique=True, nullable=False)
    total_score = db.Column(db.Numeric(5, 2), nullable=False)  # 0 to 100
    letter_grade = db.Column(db.String(5), nullable=False)  # A, B+, B, C, D, F
    grade_points = db.Column(db.Numeric(3, 2), nullable=False)  # 4.0, 3.5, etc.
    finalized_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    enrollment = db.relationship('Enrollment', back_populates='grade')

    @property
    def student_reg(self):
        if self.enrollment and self.enrollment.student:
            return self.enrollment.student.registration_number
        return "N/A"

    @property
    def course_name(self):
        if self.enrollment and self.enrollment.section and self.enrollment.section.course:
            return f"{self.enrollment.section.course.code} - {self.enrollment.section.course.title}"
        return f"Enr #{self.enrollment_id}"

    def __repr__(self):
        return f"<Grade {self.letter_grade} ({self.grade_points}) Enrollment:{self.enrollment_id}>"


class Transcript(db.Model):
    __tablename__ = 'transcripts'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    issue_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    total_credits_earned = db.Column(db.Integer, nullable=False)
    cumulative_gpa = db.Column(db.Numeric(3, 2), nullable=False)
    remarks = db.Column(db.String(255), default='Official Academic Record', nullable=True)

    student = db.relationship('Student', back_populates='transcripts')

    def __repr__(self):
        return f"<Transcript Student:{self.student_id} CGPA:{self.cumulative_gpa}>"
