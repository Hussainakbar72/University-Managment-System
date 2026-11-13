from datetime import datetime
from app.extensions import db

class FeeType(db.Model):
    __tablename__ = 'fee_types'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)  # Tuition, Lab, Library, Hostel, Transport, Admission
    description = db.Column(db.String(255), nullable=True)

    fee_structures = db.relationship('FeeStructure', back_populates='fee_type', cascade='all, delete-orphan')
    invoice_items = db.relationship('InvoiceItem', back_populates='fee_type')

    def __repr__(self):
        return f"<FeeType {self.name}>"


class FeeStructure(db.Model):
    __tablename__ = 'fee_structures'

    id = db.Column(db.Integer, primary_key=True)
    fee_type_id = db.Column(db.Integer, db.ForeignKey('fee_types.id', ondelete='CASCADE'), nullable=False, index=True)
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id', ondelete='CASCADE'), nullable=False, index=True)
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id', ondelete='CASCADE'), nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)

    fee_type = db.relationship('FeeType', back_populates='fee_structures')
    program = db.relationship('Program', back_populates='fee_structures')
    semester = db.relationship('Semester', back_populates='fee_structures')

    __table_args__ = (
        db.UniqueConstraint('fee_type_id', 'program_id', 'semester_id', name='uq_fee_structure'),
    )

    def __repr__(self):
        return f"<FeeStructure Type:{self.fee_type_id} Program:{self.program_id} Amount:{self.amount}>"


class StudentInvoice(db.Model):
    __tablename__ = 'student_invoices'

    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id', ondelete='CASCADE'), nullable=False, index=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    paid_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    issue_date = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Unpaid', nullable=False)  # Unpaid, Partially Paid, Paid, Overdue

    student = db.relationship('Student', back_populates='invoices')
    semester = db.relationship('Semester', back_populates='student_invoices')
    items = db.relationship('InvoiceItem', back_populates='invoice', cascade='all, delete-orphan')
    payments = db.relationship('Payment', back_populates='invoice', cascade='all, delete-orphan')

    @property
    def balance(self):
        return self.total_amount - self.paid_amount

    @property
    def student_reg(self):
        return self.student.registration_number if self.student else f"Student #{self.student_id}"

    @property
    def semester_name(self):
        return self.semester.name if self.semester else 'N/A'

    def __repr__(self):
        return f"<StudentInvoice {self.invoice_number} ({self.status})>"


class InvoiceItem(db.Model):
    __tablename__ = 'invoice_items'

    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('student_invoices.id', ondelete='CASCADE'), nullable=False, index=True)
    fee_type_id = db.Column(db.Integer, db.ForeignKey('fee_types.id', ondelete='RESTRICT'), nullable=False, index=True)
    description = db.Column(db.String(150), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)

    invoice = db.relationship('StudentInvoice', back_populates='items')
    fee_type = db.relationship('FeeType', back_populates='invoice_items')

    def __repr__(self):
        return f"<InvoiceItem Invoice:{self.invoice_id} Amount:{self.amount}>"


class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(80), unique=True, nullable=False, index=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('student_invoices.id', ondelete='CASCADE'), nullable=False, index=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False)  # Bank Transfer, Card, Cash, Online
    payment_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), default='Completed', nullable=False)  # Completed, Pending, Failed

    invoice = db.relationship('StudentInvoice', back_populates='payments')

    def __repr__(self):
        return f"<Payment {self.transaction_id} Amount:{self.amount}>"


class Scholarship(db.Model):
    __tablename__ = 'scholarships'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)
    discount_percentage = db.Column(db.Numeric(5, 2), nullable=False)  # e.g., 50.00 for 50%
    eligibility_criteria = db.Column(db.Text, nullable=True)

    awards = db.relationship('ScholarshipAward', back_populates='scholarship', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Scholarship {self.name} ({self.discount_percentage}%)>"


class ScholarshipAward(db.Model):
    __tablename__ = 'scholarship_awards'

    id = db.Column(db.Integer, primary_key=True)
    scholarship_id = db.Column(db.Integer, db.ForeignKey('scholarships.id', ondelete='CASCADE'), nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    awarded_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='Active', nullable=False)  # Active, Expired, Revoked

    scholarship = db.relationship('Scholarship', back_populates='awards')
    student = db.relationship('Student', back_populates='scholarship_awards')

    __table_args__ = (
        db.UniqueConstraint('scholarship_id', 'student_id', name='uq_scholarship_student'),
    )

    def __repr__(self):
        return f"<ScholarshipAward Scholarship:{self.scholarship_id} Student:{self.student_id}>"
