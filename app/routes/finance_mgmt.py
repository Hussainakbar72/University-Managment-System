from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.utils.decorators import admin_required
from app.models.academic import Program, Semester
from app.models.auth import Student
from app.models.finance import (
    FeeType, FeeStructure, StudentInvoice, InvoiceItem, Payment, Scholarship, ScholarshipAward
)
from app.forms.finance_forms import (
    FeeTypeForm, FeeStructureForm, StudentInvoiceForm, InvoiceItemForm,
    PaymentForm, ScholarshipForm, ScholarshipAwardForm
)

finance_mgmt_bp = Blueprint('finance_mgmt', __name__, url_prefix='/finance')

# ----------------- 1. FEE TYPES -----------------
@finance_mgmt_bp.route('/fee-types')
@login_required
def list_fee_types():
    types = FeeType.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Fee Categories / Types', items=types,
                           columns=[('ID', 'id'), ('Name', 'name'), ('Description', 'description')],
                           create_url=url_for('finance_mgmt.create_fee_type'), edit_endpoint='finance_mgmt.edit_fee_type', delete_endpoint='finance_mgmt.delete_fee_type')

@finance_mgmt_bp.route('/fee-types/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_fee_type():
    form = FeeTypeForm()
    if form.validate_on_submit():
        ft = FeeType(name=form.name.data, description=form.description.data)
        db.session.add(ft)
        db.session.commit()
        flash(f'Fee Type "{ft.name}" created!', 'success')
        return redirect(url_for('finance_mgmt.list_fee_types'))
    return render_template('crud/form.html', title='Add Fee Type', form=form, back_url=url_for('finance_mgmt.list_fee_types'))

@finance_mgmt_bp.route('/fee-types/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_fee_type(id):
    ft = FeeType.query.get_or_404(id)
    form = FeeTypeForm(obj=ft)
    if form.validate_on_submit():
        form.populate_obj(ft)
        db.session.commit()
        flash('Fee Type updated!', 'success')
        return redirect(url_for('finance_mgmt.list_fee_types'))
    return render_template('crud/form.html', title='Edit Fee Type', form=form, back_url=url_for('finance_mgmt.list_fee_types'))

@finance_mgmt_bp.route('/fee-types/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_fee_type(id):
    ft = FeeType.query.get_or_404(id)
    db.session.delete(ft)
    db.session.commit()
    flash('Fee Type deleted.', 'info')
    return redirect(url_for('finance_mgmt.list_fee_types'))


# ----------------- 2. FEE STRUCTURES -----------------
@finance_mgmt_bp.route('/structures')
@login_required
def list_fee_structures():
    structures = FeeStructure.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Program Fee Structures', items=structures,
                           columns=[('ID', 'id'), ('Fee Type ID', 'fee_type_id'), ('Program ID', 'program_id'), ('Semester ID', 'semester_id'), ('Amount ($)', 'amount')],
                           create_url=url_for('finance_mgmt.create_fee_structure'), edit_endpoint='finance_mgmt.edit_fee_structure', delete_endpoint='finance_mgmt.delete_fee_structure')

@finance_mgmt_bp.route('/structures/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_fee_structure():
    form = FeeStructureForm()
    form.fee_type_id.choices = [(ft.id, ft.name) for ft in FeeType.query.all()]
    form.program_id.choices = [(p.id, p.name) for p in Program.query.all()]
    form.semester_id.choices = [(s.id, s.name) for s in Semester.query.all()]
    if form.validate_on_submit():
        fs = FeeStructure(fee_type_id=form.fee_type_id.data, program_id=form.program_id.data, semester_id=form.semester_id.data, amount=form.amount.data)
        db.session.add(fs)
        db.session.commit()
        flash('Fee Structure created!', 'success')
        return redirect(url_for('finance_mgmt.list_fee_structures'))
    return render_template('crud/form.html', title='Add Fee Structure', form=form, back_url=url_for('finance_mgmt.list_fee_structures'))

@finance_mgmt_bp.route('/structures/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_fee_structure(id):
    fs = FeeStructure.query.get_or_404(id)
    form = FeeStructureForm(obj=fs)
    form.fee_type_id.choices = [(ft.id, ft.name) for ft in FeeType.query.all()]
    form.program_id.choices = [(p.id, p.name) for p in Program.query.all()]
    form.semester_id.choices = [(s.id, s.name) for s in Semester.query.all()]
    if form.validate_on_submit():
        form.populate_obj(fs)
        db.session.commit()
        flash('Fee Structure updated!', 'success')
        return redirect(url_for('finance_mgmt.list_fee_structures'))
    return render_template('crud/form.html', title='Edit Fee Structure', form=form, back_url=url_for('finance_mgmt.list_fee_structures'))

@finance_mgmt_bp.route('/structures/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_fee_structure(id):
    fs = FeeStructure.query.get_or_404(id)
    db.session.delete(fs)
    db.session.commit()
    flash('Fee Structure deleted.', 'info')
    return redirect(url_for('finance_mgmt.list_fee_structures'))


# ----------------- 3. STUDENT INVOICES -----------------
@finance_mgmt_bp.route('/invoices')
@login_required
def list_invoices():
    query = StudentInvoice.query
    if current_user.has_role('STUDENT') and current_user.student_profile:
        query = query.filter_by(student_id=current_user.student_profile.id)
    invoices = query.order_by(StudentInvoice.issue_date.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Student Fee Invoices', items=invoices,
                           columns=[('ID', 'id'), ('Invoice #', 'invoice_number'), ('Student Reg #', 'student_reg'), ('Semester', 'semester_name'), ('Total (PKR)', 'total_amount'), ('Paid (PKR)', 'paid_amount'), ('Due Date', 'due_date'), ('Status', 'status')],
                           create_url=url_for('finance_mgmt.create_invoice'), edit_endpoint='finance_mgmt.edit_invoice', delete_endpoint='finance_mgmt.delete_invoice')

@finance_mgmt_bp.route('/invoices/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_invoice():
    form = StudentInvoiceForm()
    form.student_id.choices = [(s.id, f"{s.registration_number}") for s in Student.query.all()]
    form.semester_id.choices = [(sem.id, sem.name) for sem in Semester.query.all()]
    if form.validate_on_submit():
        inv = StudentInvoice(invoice_number=form.invoice_number.data.strip().upper(), student_id=form.student_id.data, semester_id=form.semester_id.data, total_amount=form.total_amount.data, paid_amount=form.paid_amount.data, issue_date=form.issue_date.data, due_date=form.due_date.data, status=form.status.data)
        db.session.add(inv)
        db.session.commit()
        flash(f'Invoice "{inv.invoice_number}" created!', 'success')
        return redirect(url_for('finance_mgmt.list_invoices'))
    return render_template('crud/form.html', title='Generate Student Invoice', form=form, back_url=url_for('finance_mgmt.list_invoices'))

@finance_mgmt_bp.route('/invoices/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_invoice(id):
    inv = StudentInvoice.query.get_or_404(id)
    form = StudentInvoiceForm(obj=inv)
    form.student_id.choices = [(s.id, f"{s.registration_number}") for s in Student.query.all()]
    form.semester_id.choices = [(sem.id, sem.name) for sem in Semester.query.all()]
    if form.validate_on_submit():
        form.populate_obj(inv)
        db.session.commit()
        flash('Invoice updated!', 'success')
        return redirect(url_for('finance_mgmt.list_invoices'))
    return render_template('crud/form.html', title='Edit Invoice', form=form, back_url=url_for('finance_mgmt.list_invoices'))

@finance_mgmt_bp.route('/invoices/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_invoice(id):
    inv = StudentInvoice.query.get_or_404(id)
    db.session.delete(inv)
    db.session.commit()
    flash('Invoice deleted.', 'info')
    return redirect(url_for('finance_mgmt.list_invoices'))


# ----------------- 4. INVOICE ITEMS -----------------
@finance_mgmt_bp.route('/invoice-items')
@login_required
def list_invoice_items():
    items = InvoiceItem.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Invoice Line Items', items=items,
                           columns=[('ID', 'id'), ('Invoice ID', 'invoice_id'), ('Fee Type ID', 'fee_type_id'), ('Description', 'description'), ('Amount ($)', 'amount')],
                           create_url=url_for('finance_mgmt.create_invoice_item'), edit_endpoint='finance_mgmt.edit_invoice_item', delete_endpoint='finance_mgmt.delete_invoice_item')

@finance_mgmt_bp.route('/invoice-items/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_invoice_item():
    form = InvoiceItemForm()
    form.invoice_id.choices = [(inv.id, f"Invoice #{inv.invoice_number}") for inv in StudentInvoice.query.all()]
    form.fee_type_id.choices = [(ft.id, ft.name) for ft in FeeType.query.all()]
    if form.validate_on_submit():
        item = InvoiceItem(invoice_id=form.invoice_id.data, fee_type_id=form.fee_type_id.data, description=form.description.data, amount=form.amount.data)
        db.session.add(item)
        # Recalculate invoice total
        inv = StudentInvoice.query.get(form.invoice_id.data)
        if inv:
            inv.total_amount = (inv.total_amount or 0) + form.amount.data
        db.session.commit()
        flash('Line item added and invoice total updated!', 'success')
        return redirect(url_for('finance_mgmt.list_invoice_items'))
    return render_template('crud/form.html', title='Add Invoice Line Item', form=form, back_url=url_for('finance_mgmt.list_invoice_items'))

@finance_mgmt_bp.route('/invoice-items/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_invoice_item(id):
    item = InvoiceItem.query.get_or_404(id)
    form = InvoiceItemForm(obj=item)
    form.invoice_id.choices = [(inv.id, f"Invoice #{inv.invoice_number}") for inv in StudentInvoice.query.all()]
    form.fee_type_id.choices = [(ft.id, ft.name) for ft in FeeType.query.all()]
    if form.validate_on_submit():
        form.populate_obj(item)
        db.session.commit()
        flash('Invoice item updated!', 'success')
        return redirect(url_for('finance_mgmt.list_invoice_items'))
    return render_template('crud/form.html', title='Edit Invoice Item', form=form, back_url=url_for('finance_mgmt.list_invoice_items'))

@finance_mgmt_bp.route('/invoice-items/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_invoice_item(id):
    item = InvoiceItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash('Invoice item deleted.', 'info')
    return redirect(url_for('finance_mgmt.list_invoice_items'))


# ----------------- 5. PAYMENTS -----------------
@finance_mgmt_bp.route('/payments')
@login_required
def list_payments():
    payments = Payment.query.order_by(Payment.payment_date.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Fee Payments', items=payments,
                           columns=[('ID', 'id'), ('Transaction ID', 'transaction_id'), ('Invoice ID', 'invoice_id'), ('Amount ($)', 'amount'), ('Method', 'payment_method'), ('Date', 'payment_date'), ('Status', 'status')],
                           create_url=url_for('finance_mgmt.create_payment'), edit_endpoint='finance_mgmt.edit_payment', delete_endpoint='finance_mgmt.delete_payment')

@finance_mgmt_bp.route('/payments/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_payment():
    form = PaymentForm()
    form.invoice_id.choices = [(inv.id, f"Invoice #{inv.invoice_number} (Bal: ${inv.balance})") for inv in StudentInvoice.query.all()]
    if form.validate_on_submit():
        pay = Payment(transaction_id=form.transaction_id.data.strip(), invoice_id=form.invoice_id.data, amount=form.amount.data, payment_method=form.payment_method.data, status=form.status.data)
        db.session.add(pay)
        if form.status.data == 'Completed':
            inv = StudentInvoice.query.get(form.invoice_id.data)
            if inv:
                inv.paid_amount = (inv.paid_amount or 0) + form.amount.data
                if inv.paid_amount >= inv.total_amount:
                    inv.status = 'Paid'
                elif inv.paid_amount > 0:
                    inv.status = 'Partially Paid'
        db.session.commit()
        flash(f'Payment "{pay.transaction_id}" recorded!', 'success')
        return redirect(url_for('finance_mgmt.list_payments'))
    return render_template('crud/form.html', title='Record Payment', form=form, back_url=url_for('finance_mgmt.list_payments'))

@finance_mgmt_bp.route('/payments/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_payment(id):
    pay = Payment.query.get_or_404(id)
    form = PaymentForm(obj=pay)
    form.invoice_id.choices = [(inv.id, f"Invoice #{inv.invoice_number}") for inv in StudentInvoice.query.all()]
    if form.validate_on_submit():
        form.populate_obj(pay)
        db.session.commit()
        flash('Payment updated!', 'success')
        return redirect(url_for('finance_mgmt.list_payments'))
    return render_template('crud/form.html', title='Edit Payment', form=form, back_url=url_for('finance_mgmt.list_payments'))

@finance_mgmt_bp.route('/payments/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_payment(id):
    pay = Payment.query.get_or_404(id)
    db.session.delete(pay)
    db.session.commit()
    flash('Payment removed.', 'info')
    return redirect(url_for('finance_mgmt.list_payments'))


# ----------------- 6. SCHOLARSHIPS -----------------
@finance_mgmt_bp.route('/scholarships')
@login_required
def list_scholarships():
    scholars = Scholarship.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Scholarships & Grants', items=scholars,
                           columns=[('ID', 'id'), ('Name', 'name'), ('Discount %', 'discount_percentage'), ('Description', 'description')],
                           create_url=url_for('finance_mgmt.create_scholarship'), edit_endpoint='finance_mgmt.edit_scholarship', delete_endpoint='finance_mgmt.delete_scholarship')

@finance_mgmt_bp.route('/scholarships/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_scholarship():
    form = ScholarshipForm()
    if form.validate_on_submit():
        sc = Scholarship(name=form.name.data, description=form.description.data, discount_percentage=form.discount_percentage.data, eligibility_criteria=form.eligibility_criteria.data)
        db.session.add(sc)
        db.session.commit()
        flash(f'Scholarship "{sc.name}" created!', 'success')
        return redirect(url_for('finance_mgmt.list_scholarships'))
    return render_template('crud/form.html', title='Create Scholarship', form=form, back_url=url_for('finance_mgmt.list_scholarships'))

@finance_mgmt_bp.route('/scholarships/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_scholarship(id):
    sc = Scholarship.query.get_or_404(id)
    form = ScholarshipForm(obj=sc)
    if form.validate_on_submit():
        form.populate_obj(sc)
        db.session.commit()
        flash('Scholarship updated!', 'success')
        return redirect(url_for('finance_mgmt.list_scholarships'))
    return render_template('crud/form.html', title='Edit Scholarship', form=form, back_url=url_for('finance_mgmt.list_scholarships'))

@finance_mgmt_bp.route('/scholarships/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_scholarship(id):
    sc = Scholarship.query.get_or_404(id)
    db.session.delete(sc)
    db.session.commit()
    flash('Scholarship deleted.', 'info')
    return redirect(url_for('finance_mgmt.list_scholarships'))


# ----------------- 7. SCHOLARSHIP AWARDS -----------------
@finance_mgmt_bp.route('/awards')
@login_required
def list_awards():
    awards = ScholarshipAward.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Awarded Scholarships', items=awards,
                           columns=[('ID', 'id'), ('Scholarship ID', 'scholarship_id'), ('Student ID', 'student_id'), ('Awarded Date', 'awarded_date'), ('Status', 'status')],
                           create_url=url_for('finance_mgmt.create_award'), edit_endpoint='finance_mgmt.edit_award', delete_endpoint='finance_mgmt.delete_award')

@finance_mgmt_bp.route('/awards/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_award():
    form = ScholarshipAwardForm()
    form.scholarship_id.choices = [(s.id, f"{s.name} ({s.discount_percentage}%)") for s in Scholarship.query.all()]
    form.student_id.choices = [(s.id, f"{s.registration_number}") for s in Student.query.all()]
    if form.validate_on_submit():
        award = ScholarshipAward(scholarship_id=form.scholarship_id.data, student_id=form.student_id.data, awarded_date=form.awarded_date.data, status=form.status.data)
        db.session.add(award)
        db.session.commit()
        flash('Scholarship awarded successfully!', 'success')
        return redirect(url_for('finance_mgmt.list_awards'))
    return render_template('crud/form.html', title='Award Scholarship', form=form, back_url=url_for('finance_mgmt.list_awards'))

@finance_mgmt_bp.route('/awards/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_award(id):
    award = ScholarshipAward.query.get_or_404(id)
    form = ScholarshipAwardForm(obj=award)
    form.scholarship_id.choices = [(s.id, f"{s.name}") for s in Scholarship.query.all()]
    form.student_id.choices = [(s.id, f"{s.registration_number}") for s in Student.query.all()]
    if form.validate_on_submit():
        form.populate_obj(award)
        db.session.commit()
        flash('Award updated!', 'success')
        return redirect(url_for('finance_mgmt.list_awards'))
    return render_template('crud/form.html', title='Edit Award', form=form, back_url=url_for('finance_mgmt.list_awards'))

@finance_mgmt_bp.route('/awards/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_award(id):
    award = ScholarshipAward.query.get_or_404(id)
    db.session.delete(award)
    db.session.commit()
    flash('Award removed.', 'info')
    return redirect(url_for('finance_mgmt.list_awards'))
