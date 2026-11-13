from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, DateField, TimeField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class ClassroomForm(FlaskForm):
    campus_id = SelectField('Campus', coerce=int, validators=[DataRequired()])
    building_name = StringField('Building Name', validators=[DataRequired(), Length(max=100)])
    room_number = StringField('Room Number (e.g., Lab 3, Hall A)', validators=[DataRequired(), Length(max=50)])
    capacity = IntegerField('Seating Capacity', validators=[DataRequired(), NumberRange(min=1, max=1000)])
    room_type = SelectField('Room Type', choices=[
        ('Lecture Hall', 'Lecture Hall'),
        ('Computer Lab', 'Computer Lab'),
        ('Physics Lab', 'Physics Lab'),
        ('Seminar Room', 'Seminar Room')
    ], default='Lecture Hall', validators=[DataRequired()])
    submit = SubmitField('Save Classroom')

class CourseSectionForm(FlaskForm):
    section_name = StringField('Section Name (e.g., A, B, Section-1)', validators=[DataRequired(), Length(max=20)])
    course_id = SelectField('Course', coerce=int, validators=[DataRequired()])
    semester_id = SelectField('Semester', coerce=int, validators=[DataRequired()])
    instructor_id = SelectField('Instructor', coerce=int, validators=[Optional()])
    max_capacity = IntegerField('Max Capacity', default=50, validators=[DataRequired(), NumberRange(min=1, max=300)])
    submit = SubmitField('Save Course Section')

class SectionScheduleForm(FlaskForm):
    section_id = SelectField('Course Section', coerce=int, validators=[DataRequired()])
    classroom_id = SelectField('Classroom', coerce=int, validators=[Optional()])
    day_of_week = SelectField('Day of Week', choices=[
        ('Monday', 'Monday'), ('Tuesday', 'Tuesday'), ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'), ('Friday', 'Friday'), ('Saturday', 'Saturday')
    ], validators=[DataRequired()])
    start_time = TimeField('Start Time (HH:MM)', validators=[DataRequired()])
    end_time = TimeField('End Time (HH:MM)', validators=[DataRequired()])
    submit = SubmitField('Save Schedule Slot')

class EnrollmentForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    section_id = SelectField('Course Section', coerce=int, validators=[DataRequired()])
    status = SelectField('Enrollment Status', choices=[
        ('Enrolled', 'Enrolled'),
        ('Dropped', 'Dropped'),
        ('Withdrawn', 'Withdrawn'),
        ('Completed', 'Completed')
    ], default='Enrolled', validators=[DataRequired()])
    submit = SubmitField('Save Enrollment')

class AttendanceForm(FlaskForm):
    enrollment_id = SelectField('Enrolled Student', coerce=int, validators=[DataRequired()])
    schedule_id = SelectField('Class Schedule Slot', coerce=int, validators=[Optional()])
    date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    status = SelectField('Attendance Status', choices=[
        ('Present', 'Present'),
        ('Absent', 'Absent'),
        ('Late', 'Late'),
        ('Excused', 'Excused')
    ], default='Present', validators=[DataRequired()])
    remarks = TextAreaField('Remarks', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Record Attendance')
