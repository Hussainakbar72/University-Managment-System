from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange

class FeeTypeForm(FlaskForm):
    name = StringField('Fee Type Name (e.g., Tuition Fee, Lab Charges)', validators=[DataRequired(), Length(max=100)])
    description = StringField('Description', validators=[Optional(), Length(max=255)])
    submit = SubmitField('Save Fee Type')

class FeeStructureForm(FlaskForm):
    fee_type_id = SelectField('Fee Type', coerce=int, validators=[DataRequired()])
    program_id = SelectField('Program', coerce=int, validators=[DataRequired()])
    semester_id = SelectField('Semester', coerce=int, validators=[DataRequired()])
    amount = DecimalField('Amount ($)', places=2, validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Save Fee Structure')

class StudentInvoiceForm(FlaskForm):
    invoice_number = StringField('Invoice # (e.g., INV-2025-001)', validators=[DataRequired(), Length(max=50)])
    student_id = SelectField('Student', coerce=int, validators=[DataRequired()])
    semester_id = SelectField('Semester', coerce=int, validators=[DataRequired()])
    total_amount = DecimalField('Total Amount ($)', places=2, default=0.00, validators=[DataRequired(), NumberRange(min=0)])
    paid_amount = DecimalField('Paid Amount ($)', places=2, default=0.00, validators=[DataRequired(), NumberRange(min=0)])
    issue_date = DateField('Issue Date', format='%Y-%m-%d', validators=[DataRequired()])
    due_date = DateField('Due Date', format='%Y-%m-%d', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('Unpaid', 'Unpaid'), ('Partially Paid', 'Partially Paid'),
        ('Paid', 'Paid'), ('Overdue', 'Overdue')
    ], default='Unpaid', validators=[DataRequired()])
    submit = SubmitField('Save Invoice')

class InvoiceItemForm(FlaskForm):
    invoice_id = SelectField('Invoice', coerce=int, validators=[DataRequired()])
    fee_type_id = SelectField('Fee Type', coerce=int, validators=[DataRequired()])
    description = StringField('Line Item Description', validators=[DataRequired(), Length(max=150)])
    amount = DecimalField('Item Amount ($)', places=2, validators=[DataRequired(), NumberRange(min=0)])
    submit = SubmitField('Add Item to Invoice')

class PaymentForm(FlaskForm):
    transaction_id = StringField('Transaction ID / Receipt #', validators=[DataRequired(), Length(max=80)])
    invoice_id = SelectField('Target Invoice', coerce=int, validators=[DataRequired()])
    amount = DecimalField('Payment Amount ($)', places=2, validators=[DataRequired(), NumberRange(min=0.01)])
    payment_method = SelectField('Payment Method', choices=[
        ('Bank Transfer', 'Bank Transfer'), ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'), ('Cash', 'Cash'), ('Online Portal', 'Online Portal')
    ], validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('Completed', 'Completed'), ('Pending', 'Pending'), ('Failed', 'Failed')
    ], default='Completed', validators=[DataRequired()])
    submit = SubmitField('Process Payment')

class ScholarshipForm(FlaskForm):
    name = StringField('Scholarship Name', validators=[DataRequired(), Length(max=120)])
    description = TextAreaField('Description', validators=[Optional()])
    discount_percentage = DecimalField('Discount Percentage %', places=2, validators=[DataRequired(), NumberRange(min=1, max=100)])
    eligibility_criteria = TextAreaField('Eligibility Criteria', validators=[Optional()])
    submit = SubmitField('Save Scholarship')

class ScholarshipAwardForm(FlaskForm):
    scholarship_id = SelectField('Scholarship', coerce=int, validators=[DataRequired()])
    student_id = SelectField('Student Recipient', coerce=int, validators=[DataRequired()])
    awarded_date = DateField('Awarded Date', format='%Y-%m-%d', validators=[DataRequired()])
    status = SelectField('Status', choices=[('Active', 'Active'), ('Expired', 'Expired'), ('Revoked', 'Revoked')], default='Active')
    submit = SubmitField('Award Scholarship')
