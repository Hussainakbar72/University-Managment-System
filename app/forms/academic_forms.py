from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, BooleanField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class CampusForm(FlaskForm):
    name = StringField('Campus Name', validators=[DataRequired(), Length(max=120)])
    code = StringField('Campus Code', validators=[DataRequired(), Length(max=20)])
    address = TextAreaField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired(), Length(max=60)])
    is_main = BooleanField('Is Main Campus')
    submit = SubmitField('Save Campus')

class FacultyForm(FlaskForm):
    name = StringField('Faculty Name', validators=[DataRequired(), Length(max=120)])
    code = StringField('Faculty Code', validators=[DataRequired(), Length(max=20)])
    campus_id = SelectField('Campus', coerce=int, validators=[DataRequired()])
    dean_name = StringField('Dean Name', validators=[Optional(), Length(max=120)])
    submit = SubmitField('Save Faculty')

class DepartmentForm(FlaskForm):
    name = StringField('Department Name', validators=[DataRequired(), Length(max=120)])
    code = StringField('Department Code', validators=[DataRequired(), Length(max=20)])
    faculty_id = SelectField('Faculty', coerce=int, validators=[DataRequired()])
    head_of_department = StringField('Head of Department', validators=[Optional(), Length(max=120)])
    submit = SubmitField('Save Department')

class ProgramForm(FlaskForm):
    name = StringField('Program Name', validators=[DataRequired(), Length(max=120)])
    code = StringField('Program Code', validators=[DataRequired(), Length(max=20)])
    department_id = SelectField('Department', coerce=int, validators=[DataRequired()])
    degree_type = SelectField('Degree Type', choices=[('BS', 'BS'), ('MS', 'MS'), ('PhD', 'PhD'), ('Diploma', 'Diploma')], validators=[DataRequired()])
    total_credit_hours = IntegerField('Total Credit Hours', validators=[DataRequired(), NumberRange(min=1, max=300)])
    duration_years = IntegerField('Duration (Years)', validators=[DataRequired(), NumberRange(min=1, max=10)])
    submit = SubmitField('Save Program')

class AcademicYearForm(FlaskForm):
    year_name = StringField('Academic Year (e.g., 2025-2026)', validators=[DataRequired(), Length(max=50)])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    is_current = BooleanField('Current Academic Year')
    submit = SubmitField('Save Academic Year')

class SemesterForm(FlaskForm):
    name = StringField('Semester Name (e.g., Fall 2025)', validators=[DataRequired(), Length(max=50)])
    academic_year_id = SelectField('Academic Year', coerce=int, validators=[DataRequired()])
    start_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    end_date = DateField('End Date', format='%Y-%m-%d', validators=[DataRequired()])
    is_active = BooleanField('Is Active')
    submit = SubmitField('Save Semester')

class CourseForm(FlaskForm):
    code = StringField('Course Code (e.g., CS-101)', validators=[DataRequired(), Length(max=20)])
    title = StringField('Course Title', validators=[DataRequired(), Length(max=150)])
    credit_hours = IntegerField('Credit Hours', validators=[DataRequired(), NumberRange(min=1, max=6)])
    department_id = SelectField('Department (Teaching Department)', coerce=int, validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save Course')

class CoursePrerequisiteForm(FlaskForm):
    course_id = SelectField('Target Course', coerce=int, validators=[DataRequired()])
    prerequisite_id = SelectField('Prerequisite Course Required', coerce=int, validators=[DataRequired()])
    minimum_grade = SelectField('Minimum Grade Required', choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')], default='D', validators=[DataRequired()])
    submit = SubmitField('Assign Prerequisite')
