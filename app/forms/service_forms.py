from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, IntegerField, SelectField, DateField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

# --- Library Forms ---
class LibraryBookForm(FlaskForm):
    isbn = StringField('ISBN Number', validators=[DataRequired(), Length(max=30)])
    title = StringField('Book Title', validators=[DataRequired(), Length(max=200)])
    author = StringField('Author(s)', validators=[DataRequired(), Length(max=150)])
    publisher = StringField('Publisher', validators=[Optional(), Length(max=100)])
    publication_year = IntegerField('Publication Year', validators=[Optional(), NumberRange(min=1800, max=2100)])
    category = StringField('Category / Subject', validators=[DataRequired(), Length(max=80)])
    submit = SubmitField('Save Book')

class BookCopyForm(FlaskForm):
    book_id = SelectField('Book', coerce=int, validators=[DataRequired()])
    barcode = StringField('Barcode / Asset Tag', validators=[DataRequired(), Length(max=50)])
    status = SelectField('Copy Status', choices=[
        ('Available', 'Available'), ('Borrowed', 'Borrowed'),
        ('Lost', 'Lost'), ('Maintenance', 'Maintenance')
    ], default='Available', validators=[DataRequired()])
    shelf_location = StringField('Shelf Location (e.g., Row 4, Shelf B)', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Save Book Copy')

class LibraryLoanForm(FlaskForm):
    book_copy_id = SelectField('Book Copy', coerce=int, validators=[DataRequired()])
    user_id = SelectField('Borrower (User)', coerce=int, validators=[DataRequired()])
    borrow_date = DateField('Borrow Date', format='%Y-%m-%d', validators=[DataRequired()])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[DataRequired()])
    return_date = DateField('Return Date', format='%Y-%m-%d', validators=[Optional()])
    status = SelectField('Loan Status', choices=[('Active', 'Active'), ('Returned', 'Returned'), ('Overdue', 'Overdue')], default='Active')
    submit = SubmitField('Issue / Update Loan')

class LibraryFineForm(FlaskForm):
    loan_id = SelectField('Library Loan Record', coerce=int, validators=[DataRequired()])
    amount = DecimalField('Fine Amount ($)', places=2, validators=[DataRequired(), NumberRange(min=0.01)])
    status = SelectField('Status', choices=[('Unpaid', 'Unpaid'), ('Paid', 'Paid'), ('Waived', 'Waived')], default='Unpaid')
    submit = SubmitField('Save Fine Record')

# --- Hostel Forms ---
class HostelBuildingForm(FlaskForm):
    name = StringField('Building Name / Hall', validators=[DataRequired(), Length(max=100)])
    campus_id = SelectField('Campus', coerce=int, validators=[DataRequired()])
    gender_type = SelectField('Hostel Type', choices=[('Male', 'Male Hostel'), ('Female', 'Female Hostel'), ('Mixed', 'Faculty/Guest Hostel')], validators=[DataRequired()])
    warden_name = StringField('Warden / Manager Name', validators=[Optional(), Length(max=120)])
    total_floors = IntegerField('Total Floors', default=3, validators=[DataRequired(), NumberRange(min=1, max=20)])
    submit = SubmitField('Save Hostel Building')

class HostelRoomForm(FlaskForm):
    building_id = SelectField('Building', coerce=int, validators=[DataRequired()])
    room_number = StringField('Room Number (e.g., 101, 204)', validators=[DataRequired(), Length(max=30)])
    capacity = IntegerField('Bed Capacity', default=2, validators=[DataRequired(), NumberRange(min=1, max=10)])
    monthly_fee = DecimalField('Monthly Fee ($)', places=2, validators=[DataRequired(), NumberRange(min=0)])
    room_type = SelectField('Room Type', choices=[('Standard', 'Standard'), ('Deluxe', 'Deluxe'), ('Cubicle', 'Cubicle')], default='Standard')
    submit = SubmitField('Save Hostel Room')

class HostelAllocationForm(FlaskForm):
    room_id = SelectField('Hostel Room', coerce=int, validators=[DataRequired()])
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    allocated_date = DateField('Allocation Date', format='%Y-%m-%d', validators=[DataRequired()])
    vacated_date = DateField('Vacated Date', format='%Y-%m-%d', validators=[Optional()])
    status = SelectField('Status', choices=[('Active', 'Active'), ('Vacated', 'Vacated'), ('Suspended', 'Suspended')], default='Active')
    submit = SubmitField('Save Allocation')

# --- Transport Forms ---
class TransportRouteForm(FlaskForm):
    route_name = StringField('Route Name (e.g., Route 1 - Downtown)', validators=[DataRequired(), Length(max=100)])
    start_point = StringField('Starting Point', validators=[DataRequired(), Length(max=120)])
    end_point = StringField('Destination / Campus', validators=[DataRequired(), Length(max=120)])
    stops_description = TextAreaField('Major Stops (comma-separated)', validators=[Optional()])
    monthly_fare = DecimalField('Monthly Bus Fare ($)', places=2, validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save Route')

class TransportVehicleForm(FlaskForm):
    vehicle_number = StringField('Vehicle Plate # (e.g., BUS-501)', validators=[DataRequired(), Length(max=30)])
    route_id = SelectField('Assigned Route', coerce=int, validators=[Optional()])
    capacity = IntegerField('Passenger Capacity', default=40, validators=[DataRequired(), NumberRange(min=1, max=100)])
    driver_name = StringField('Driver Name', validators=[DataRequired(), Length(max=100)])
    driver_phone = StringField('Driver Contact Phone', validators=[DataRequired(), Length(max=30)])
    status = SelectField('Status', choices=[('Active', 'Active'), ('Maintenance', 'Maintenance'), ('Out of Service', 'Out of Service')], default='Active')
    submit = SubmitField('Save Vehicle')

class TransportAssignmentForm(FlaskForm):
    vehicle_id = SelectField('Vehicle', coerce=int, validators=[DataRequired()])
    user_id = SelectField('Passenger (Student / Staff)', coerce=int, validators=[DataRequired()])
    pickup_stop = StringField('Designated Pickup Stop', validators=[DataRequired(), Length(max=120)])
    assigned_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Active', 'Active'), ('Cancelled', 'Cancelled')], default='Active')
    submit = SubmitField('Save Bus Pass Assignment')

# --- System & Notification Forms ---
class AnnouncementForm(FlaskForm):
    title = StringField('Announcement Title', validators=[DataRequired(), Length(max=150)])
    target_audience = SelectField('Target Audience', choices=[('All', 'Everyone'), ('Students', 'Students Only'), ('Instructors', 'Instructors Only'), ('Staff', 'Staff Only')], default='All')
    content = TextAreaField('Announcement Message', validators=[DataRequired()])
    is_published = BooleanField('Published Immediately', default=True)
    submit = SubmitField('Publish Announcement')

class NotificationForm(FlaskForm):
    user_id = SelectField('Target User', coerce=int, validators=[DataRequired()])
    title = StringField('Notification Title', validators=[DataRequired(), Length(max=150)])
    message = TextAreaField('Message Body', validators=[DataRequired()])
    is_read = BooleanField('Mark as Read', default=False)
    submit = SubmitField('Send Notification')

class AuditLogForm(FlaskForm):
    user_id = SelectField('User Initiator', coerce=int, validators=[Optional()])
    action = StringField('Action Tag', validators=[DataRequired(), Length(max=100)])
    table_name = StringField('Table Name', validators=[DataRequired(), Length(max=50)])
    record_id = IntegerField('Record ID', validators=[Optional()])
    ip_address = StringField('IP Address', validators=[Optional(), Length(max=45)])
    details = TextAreaField('Audit Details', validators=[Optional()])
    submit = SubmitField('Log Entry')
