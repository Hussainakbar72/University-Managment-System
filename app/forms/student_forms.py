from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SelectField, DateField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Email, NumberRange

class StudentForm(FlaskForm):
    user_id = SelectField('User Account', coerce=int, validators=[DataRequired()])
    registration_number = StringField('Registration Number (e.g., FA24-BCS-001)', validators=[DataRequired(), Length(max=50)])
    program_id = SelectField('Academic Program', coerce=int, validators=[DataRequired()])
    admission_date = DateField('Admission Date', format='%Y-%m-%d', validators=[DataRequired()])
    current_semester = IntegerField('Current Semester', default=1, validators=[DataRequired(), NumberRange(min=1, max=12)])
    status = SelectField('Status', choices=[('Active', 'Active'), ('Suspended', 'Suspended'), ('Graduated', 'Graduated'), ('Inactive', 'Inactive')], default='Active')
    cgpa = DecimalField('CGPA', default=0.00, places=2, validators=[Optional(), NumberRange(min=0.00, max=4.00)])
    submit = SubmitField('Save Student')

class InstructorForm(FlaskForm):
    user_id = SelectField('User Account', coerce=int, validators=[DataRequired()])
    employee_id = SelectField if False else StringField('Employee ID (e.g., EMP-INS-101)', validators=[DataRequired(), Length(max=50)])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    designation = SelectField('Designation', choices=[
        ('Professor', 'Professor'),
        ('Associate Professor', 'Associate Professor'),
        ('Assistant Professor', 'Assistant Professor'),
        ('Lecturer', 'Lecturer'),
        ('Adjunct Faculty', 'Adjunct Faculty')
    ], validators=[DataRequired()])
    qualification = StringField('Highest Qualification (e.g., PhD CS)', validators=[Optional(), Length(max=120)])
    joining_date = DateField('Joining Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Save Instructor')

class StaffForm(FlaskForm):
    user_id = SelectField('User Account', coerce=int, validators=[DataRequired()])
    employee_id = StringField('Employee ID', validators=[DataRequired(), Length(max=50)])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    job_title = StringField('Job Title', validators=[DataRequired(), Length(max=100)])
    hire_date = DateField('Hire Date', format='%Y-%m-%d', validators=[DataRequired()])
    submit = SubmitField('Save Staff Member')

class GuardianForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(max=120)])
    relationship = SelectField('Relationship', choices=[('Father', 'Father'), ('Mother', 'Mother'), ('Brother', 'Brother'), ('Uncle', 'Uncle'), ('Guardian', 'Guardian')], validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(max=30)])
    email = StringField('Email Address', validators=[Optional(), Email(), Length(max=120)])
    occupation = StringField('Occupation', validators=[Optional(), Length(max=100)])
    address = TextAreaField('Residential Address', validators=[Optional()])
    submit = SubmitField('Save Guardian')

class StudentGuardianForm(FlaskForm):
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    guardian_id = SelectField('Guardian', coerce=int, validators=[DataRequired()])
    is_primary = BooleanField('Is Primary Emergency Contact')
    submit = SubmitField('Link Guardian to Student')
