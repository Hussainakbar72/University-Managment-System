from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, SelectField, DateField, TimeField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class AssessmentForm(FlaskForm):
    section_id = SelectField('Course Section', coerce=int, validators=[DataRequired()])
    title = StringField('Assessment Title', validators=[DataRequired(), Length(max=100)])
    assessment_type = SelectField('Type', choices=[
        ('Quiz', 'Quiz'), ('Assignment', 'Assignment'), ('Midterm Project', 'Midterm Project'),
        ('Lab Task', 'Lab Task'), ('Presentation', 'Presentation')
    ], validators=[DataRequired()])
    max_marks = DecimalField('Maximum Marks', places=2, validators=[DataRequired(), NumberRange(min=1)])
    weightage = DecimalField('Weightage %', places=2, validators=[DataRequired(), NumberRange(min=0, max=100)])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Save Assessment')

class AssessmentResultForm(FlaskForm):
    assessment_id = SelectField('Assessment', coerce=int, validators=[DataRequired()])
    enrollment_id = SelectField('Enrolled Student', coerce=int, validators=[DataRequired()])
    marks_obtained = DecimalField('Marks Obtained', places=2, validators=[DataRequired(), NumberRange(min=0)])
    feedback = TextAreaField('Feedback', validators=[Optional()])
    submit = SubmitField('Save Result')

class ExamForm(FlaskForm):
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    semester_id = SelectField('Semester', coerce=int, validators=[DataRequired()])
    exam_type = SelectField('Exam Type', choices=[
        ('Midterm', 'Midterm'), ('Final', 'Final'), ('Supplementary', 'Supplementary')
    ], validators=[DataRequired()])
    exam_date = DateField('Exam Date', format='%Y-%m-%d', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    duration_minutes = IntegerField('Duration (Minutes)', default=180, validators=[DataRequired(), NumberRange(min=15, max=360)])
    total_marks = DecimalField('Total Marks', default=100.00, places=2, validators=[DataRequired(), NumberRange(min=10)])
    submit = SubmitField('Save Exam Schedule')

class ExamRoomForm(FlaskForm):
    exam_id = SelectField('Exam', coerce=int, validators=[DataRequired()])
    classroom_id = SelectField('Classroom / Hall', coerce=int, validators=[DataRequired()])
    invigilator_name = StringField('Invigilator Name', validators=[Optional(), Length(max=120)])
    submit = SubmitField('Assign Exam Room')

class ExamSeatingForm(FlaskForm):
    exam_room_id = SelectField('Exam Room Assignment', coerce=int, validators=[DataRequired()])
    enrollment_id = SelectField('Student Enrollment', coerce=int, validators=[DataRequired()])
    seat_number = StringField('Desk / Seat Number', validators=[DataRequired(), Length(max=30)])
    is_attended = BooleanField('Attended Exam', default=True)
    submit = SubmitField('Save Seating Allocation')

class GradeForm(FlaskForm):
    enrollment_id = SelectField('Enrolled Student', coerce=int, validators=[DataRequired()])
    total_score = DecimalField('Total Score (0 - 100)', places=2, validators=[DataRequired(), NumberRange(min=0, max=100)])
    letter_grade = SelectField('Letter Grade', choices=[
        ('A', 'A (4.0)'), ('A-', 'A- (3.7)'), ('B+', 'B+ (3.3)'), ('B', 'B (3.0)'),
        ('B-', 'B- (2.7)'), ('C+', 'C+ (2.3)'), ('C', 'C (2.0)'), ('D', 'D (1.0)'), ('F', 'F (0.0)')
    ], validators=[DataRequired()])
    grade_points = DecimalField('Grade Points (GPA)', places=2, validators=[DataRequired(), NumberRange(min=0.00, max=4.00)])
    submit = SubmitField('Submit Final Grade')

class TranscriptForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    issue_date = DateField('Issue Date', format='%Y-%m-%d', validators=[DataRequired()])
    total_credits_earned = IntegerField('Credits Earned', validators=[DataRequired(), NumberRange(min=0, max=300)])
    cumulative_gpa = DecimalField('Cumulative GPA (CGPA)', places=2, validators=[DataRequired(), NumberRange(min=0.00, max=4.00)])
    remarks = StringField('Remarks', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Issue Transcript')
