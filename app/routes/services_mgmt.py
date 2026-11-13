from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.extensions import db
from app.utils.decorators import admin_required
from app.models.auth import User, Student
from app.models.academic import Campus
from app.models.library import LibraryBook, BookCopy, LibraryLoan, LibraryFine
from app.models.hostel import HostelBuilding, HostelRoom, HostelAllocation
from app.models.transport import TransportRoute, TransportVehicle, TransportAssignment
from app.models.system import Announcement, Notification
from app.forms.service_forms import (
    LibraryBookForm, BookCopyForm, LibraryLoanForm, LibraryFineForm,
    HostelBuildingForm, HostelRoomForm, HostelAllocationForm,
    TransportRouteForm, TransportVehicleForm, TransportAssignmentForm,
    AnnouncementForm, NotificationForm
)

services_mgmt_bp = Blueprint('services_mgmt', __name__, url_prefix='/services')

# ==================== LIBRARY MODULE ====================
# 1. BOOKS
@services_mgmt_bp.route('/library/books')
@login_required
def list_books():
    search = request.args.get('search', '').strip()
    query = LibraryBook.query
    if search:
        query = query.filter(LibraryBook.title.ilike(f'%{search}%') | LibraryBook.author.ilike(f'%{search}%') | LibraryBook.isbn.ilike(f'%{search}%'))
    books = query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Library Catalog', items=books,
                           columns=[('ID', 'id'), ('ISBN', 'isbn'), ('Title', 'title'), ('Author', 'author'), ('Category', 'category')],
                           create_url=url_for('services_mgmt.create_book'), edit_endpoint='services_mgmt.edit_book', delete_endpoint='services_mgmt.delete_book')

@services_mgmt_bp.route('/library/books/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_book():
    form = LibraryBookForm()
    if form.validate_on_submit():
        book = LibraryBook(isbn=form.isbn.data.strip(), title=form.title.data, author=form.author.data, publisher=form.publisher.data, publication_year=form.publication_year.data, category=form.category.data)
        db.session.add(book)
        db.session.commit()
        flash(f'Book "{book.title}" added to catalog!', 'success')
        return redirect(url_for('services_mgmt.list_books'))
    return render_template('crud/form.html', title='Add Library Book', form=form, back_url=url_for('services_mgmt.list_books'))

@services_mgmt_bp.route('/library/books/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_book(id):
    book = LibraryBook.query.get_or_404(id)
    form = LibraryBookForm(obj=book)
    if form.validate_on_submit():
        form.populate_obj(book)
        db.session.commit()
        flash('Book details updated!', 'success')
        return redirect(url_for('services_mgmt.list_books'))
    return render_template('crud/form.html', title='Edit Book', form=form, back_url=url_for('services_mgmt.list_books'))

@services_mgmt_bp.route('/library/books/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_book(id):
    book = LibraryBook.query.get_or_404(id)
    db.session.delete(book)
    db.session.commit()
    flash('Book removed from library.', 'info')
    return redirect(url_for('services_mgmt.list_books'))


# 2. BOOK COPIES
@services_mgmt_bp.route('/library/copies')
@login_required
def list_copies():
    copies = BookCopy.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Physical Book Copies', items=copies,
                           columns=[('ID', 'id'), ('Book ID', 'book_id'), ('Barcode', 'barcode'), ('Status', 'status'), ('Shelf', 'shelf_location')],
                           create_url=url_for('services_mgmt.create_copy'), edit_endpoint='services_mgmt.edit_copy', delete_endpoint='services_mgmt.delete_copy')

@services_mgmt_bp.route('/library/copies/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_copy():
    form = BookCopyForm()
    form.book_id.choices = [(b.id, f"{b.title} ({b.isbn})") for b in LibraryBook.query.all()]
    if form.validate_on_submit():
        copy = BookCopy(book_id=form.book_id.data, barcode=form.barcode.data.strip(), status=form.status.data, shelf_location=form.shelf_location.data)
        db.session.add(copy)
        db.session.commit()
        flash('Physical copy registered!', 'success')
        return redirect(url_for('services_mgmt.list_copies'))
    return render_template('crud/form.html', title='Add Book Copy', form=form, back_url=url_for('services_mgmt.list_copies'))

@services_mgmt_bp.route('/library/copies/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_copy(id):
    copy = BookCopy.query.get_or_404(id)
    form = BookCopyForm(obj=copy)
    form.book_id.choices = [(b.id, f"{b.title} ({b.isbn})") for b in LibraryBook.query.all()]
    if form.validate_on_submit():
        form.populate_obj(copy)
        db.session.commit()
        flash('Book copy updated!', 'success')
        return redirect(url_for('services_mgmt.list_copies'))
    return render_template('crud/form.html', title='Edit Book Copy', form=form, back_url=url_for('services_mgmt.list_copies'))

@services_mgmt_bp.route('/library/copies/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_copy(id):
    copy = BookCopy.query.get_or_404(id)
    db.session.delete(copy)
    db.session.commit()
    flash('Book copy deleted.', 'info')
    return redirect(url_for('services_mgmt.list_copies'))


# 3. LIBRARY LOANS
@services_mgmt_bp.route('/library/loans')
@login_required
def list_loans():
    query = LibraryLoan.query
    if current_user.has_role('STUDENT'):
        query = query.filter_by(user_id=current_user.id)
    loans = query.order_by(LibraryLoan.borrow_date.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Circulation / Loans', items=loans,
                           columns=[('ID', 'id'), ('Copy ID', 'book_copy_id'), ('User ID', 'user_id'), ('Borrow Date', 'borrow_date'), ('Due Date', 'due_date'), ('Status', 'status')],
                           create_url=url_for('services_mgmt.create_loan'), edit_endpoint='services_mgmt.edit_loan', delete_endpoint='services_mgmt.delete_loan')

@services_mgmt_bp.route('/library/loans/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_loan():
    form = LibraryLoanForm()
    form.book_copy_id.choices = [(c.id, f"Barcode {c.barcode} ({c.book.title if c.book else ''})") for c in BookCopy.query.all()]
    form.user_id.choices = [(u.id, f"{u.full_name} ({u.email})") for u in User.query.all()]
    if form.validate_on_submit():
        loan = LibraryLoan(book_copy_id=form.book_copy_id.data, user_id=form.user_id.data, borrow_date=form.borrow_date.data, due_date=form.due_date.data, return_date=form.return_date.data, status=form.status.data)
        db.session.add(loan)
        copy = BookCopy.query.get(form.book_copy_id.data)
        if copy:
            copy.status = 'Borrowed'
        db.session.commit()
        flash('Book loaned successfully!', 'success')
        return redirect(url_for('services_mgmt.list_loans'))
    return render_template('crud/form.html', title='Issue Library Loan', form=form, back_url=url_for('services_mgmt.list_loans'))

@services_mgmt_bp.route('/library/loans/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_loan(id):
    loan = LibraryLoan.query.get_or_404(id)
    form = LibraryLoanForm(obj=loan)
    form.book_copy_id.choices = [(c.id, f"Barcode {c.barcode} ({c.book.title if c.book else ''})") for c in BookCopy.query.all()]
    form.user_id.choices = [(u.id, f"{u.full_name} ({u.email})") for u in User.query.all()]
    if form.validate_on_submit():
        form.populate_obj(loan)
        if loan.status == 'Returned' and loan.book_copy:
            loan.book_copy.status = 'Available'
        db.session.commit()
        flash('Loan record updated!', 'success')
        return redirect(url_for('services_mgmt.list_loans'))
    return render_template('crud/form.html', title='Edit Loan', form=form, back_url=url_for('services_mgmt.list_loans'))

@services_mgmt_bp.route('/library/loans/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_loan(id):
    loan = LibraryLoan.query.get_or_404(id)
    db.session.delete(loan)
    db.session.commit()
    flash('Loan record removed.', 'info')
    return redirect(url_for('services_mgmt.list_loans'))


# 4. LIBRARY FINES
@services_mgmt_bp.route('/library/fines')
@login_required
def list_fines():
    fines = LibraryFine.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Overdue & Damage Fines', items=fines,
                           columns=[('ID', 'id'), ('Loan ID', 'loan_id'), ('Amount ($)', 'amount'), ('Status', 'status'), ('Paid Date', 'paid_date')],
                           create_url=url_for('services_mgmt.create_fine'), edit_endpoint='services_mgmt.edit_fine', delete_endpoint='services_mgmt.delete_fine')

@services_mgmt_bp.route('/library/fines/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_fine():
    form = LibraryFineForm()
    form.loan_id.choices = [(l.id, f"Loan #{l.id} (User {l.user_id})") for l in LibraryLoan.query.all()]
    if form.validate_on_submit():
        fine = LibraryFine(loan_id=form.loan_id.data, amount=form.amount.data, status=form.status.data)
        db.session.add(fine)
        db.session.commit()
        flash('Fine assessed!', 'success')
        return redirect(url_for('services_mgmt.list_fines'))
    return render_template('crud/form.html', title='Issue Fine', form=form, back_url=url_for('services_mgmt.list_fines'))

@services_mgmt_bp.route('/library/fines/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_fine(id):
    fine = LibraryFine.query.get_or_404(id)
    form = LibraryFineForm(obj=fine)
    form.loan_id.choices = [(l.id, f"Loan #{l.id} (User {l.user_id})") for l in LibraryLoan.query.all()]
    if form.validate_on_submit():
        form.populate_obj(fine)
        db.session.commit()
        flash('Fine record updated!', 'success')
        return redirect(url_for('services_mgmt.list_fines'))
    return render_template('crud/form.html', title='Edit Fine', form=form, back_url=url_for('services_mgmt.list_fines'))

@services_mgmt_bp.route('/library/fines/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_fine(id):
    fine = LibraryFine.query.get_or_404(id)
    db.session.delete(fine)
    db.session.commit()
    flash('Fine record deleted.', 'info')
    return redirect(url_for('services_mgmt.list_fines'))


# ==================== HOSTEL MODULE ====================
# 5. HOSTEL BUILDINGS
@services_mgmt_bp.route('/hostel/buildings')
@login_required
def list_hostel_buildings():
    buildings = HostelBuilding.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Hostel Halls & Buildings', items=buildings,
                           columns=[('ID', 'id'), ('Name', 'name'), ('Type', 'gender_type'), ('Warden', 'warden_name'), ('Floors', 'total_floors')],
                           create_url=url_for('services_mgmt.create_hostel_building'), edit_endpoint='services_mgmt.edit_hostel_building', delete_endpoint='services_mgmt.delete_hostel_building')

@services_mgmt_bp.route('/hostel/buildings/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_hostel_building():
    form = HostelBuildingForm()
    form.campus_id.choices = [(c.id, c.name) for c in Campus.query.all()]
    if form.validate_on_submit():
        hb = HostelBuilding(name=form.name.data, campus_id=form.campus_id.data, gender_type=form.gender_type.data, warden_name=form.warden_name.data, total_floors=form.total_floors.data)
        db.session.add(hb)
        db.session.commit()
        flash(f'Hostel building "{hb.name}" saved!', 'success')
        return redirect(url_for('services_mgmt.list_hostel_buildings'))
    return render_template('crud/form.html', title='Add Hostel Building', form=form, back_url=url_for('services_mgmt.list_hostel_buildings'))

@services_mgmt_bp.route('/hostel/buildings/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_hostel_building(id):
    hb = HostelBuilding.query.get_or_404(id)
    form = HostelBuildingForm(obj=hb)
    form.campus_id.choices = [(c.id, c.name) for c in Campus.query.all()]
    if form.validate_on_submit():
        form.populate_obj(hb)
        db.session.commit()
        flash('Hostel building updated!', 'success')
        return redirect(url_for('services_mgmt.list_hostel_buildings'))
    return render_template('crud/form.html', title='Edit Hostel Building', form=form, back_url=url_for('services_mgmt.list_hostel_buildings'))

@services_mgmt_bp.route('/hostel/buildings/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_hostel_building(id):
    hb = HostelBuilding.query.get_or_404(id)
    db.session.delete(hb)
    db.session.commit()
    flash('Hostel building deleted.', 'info')
    return redirect(url_for('services_mgmt.list_hostel_buildings'))


# 6. HOSTEL ROOMS
@services_mgmt_bp.route('/hostel/rooms')
@login_required
def list_hostel_rooms():
    rooms = HostelRoom.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Hostel Rooms', items=rooms,
                           columns=[('ID', 'id'), ('Building ID', 'building_id'), ('Room #', 'room_number'), ('Capacity', 'capacity'), ('Fee ($)', 'monthly_fee'), ('Type', 'room_type')],
                           create_url=url_for('services_mgmt.create_hostel_room'), edit_endpoint='services_mgmt.edit_hostel_room', delete_endpoint='services_mgmt.delete_hostel_room')

@services_mgmt_bp.route('/hostel/rooms/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_hostel_room():
    form = HostelRoomForm()
    form.building_id.choices = [(b.id, b.name) for b in HostelBuilding.query.all()]
    if form.validate_on_submit():
        hr = HostelRoom(building_id=form.building_id.data, room_number=form.room_number.data, capacity=form.capacity.data, monthly_fee=form.monthly_fee.data, room_type=form.room_type.data)
        db.session.add(hr)
        db.session.commit()
        flash('Hostel room added!', 'success')
        return redirect(url_for('services_mgmt.list_hostel_rooms'))
    return render_template('crud/form.html', title='Add Hostel Room', form=form, back_url=url_for('services_mgmt.list_hostel_rooms'))

@services_mgmt_bp.route('/hostel/rooms/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_hostel_room(id):
    hr = HostelRoom.query.get_or_404(id)
    form = HostelRoomForm(obj=hr)
    form.building_id.choices = [(b.id, b.name) for b in HostelBuilding.query.all()]
    if form.validate_on_submit():
        form.populate_obj(hr)
        db.session.commit()
        flash('Hostel room updated!', 'success')
        return redirect(url_for('services_mgmt.list_hostel_rooms'))
    return render_template('crud/form.html', title='Edit Hostel Room', form=form, back_url=url_for('services_mgmt.list_hostel_rooms'))

@services_mgmt_bp.route('/hostel/rooms/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_hostel_room(id):
    hr = HostelRoom.query.get_or_404(id)
    db.session.delete(hr)
    db.session.commit()
    flash('Hostel room deleted.', 'info')
    return redirect(url_for('services_mgmt.list_hostel_rooms'))


# 7. HOSTEL ALLOCATIONS
@services_mgmt_bp.route('/hostel/allocations')
@login_required
def list_hostel_allocations():
    allocations = HostelAllocation.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Hostel Bed Allocations', items=allocations,
                           columns=[('ID', 'id'), ('Room ID', 'room_id'), ('Student ID', 'student_id'), ('Allocated Date', 'allocated_date'), ('Status', 'status')],
                           create_url=url_for('services_mgmt.create_hostel_allocation'), edit_endpoint='services_mgmt.edit_hostel_allocation', delete_endpoint='services_mgmt.delete_hostel_allocation')

@services_mgmt_bp.route('/hostel/allocations/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_hostel_allocation():
    form = HostelAllocationForm()
    form.room_id.choices = [(r.id, f"Room {r.room_number} (Bld {r.building_id})") for r in HostelRoom.query.all()]
    form.student_id.choices = [(s.id, f"{s.registration_number}") for s in Student.query.all()]
    if form.validate_on_submit():
        ha = HostelAllocation(room_id=form.room_id.data, student_id=form.student_id.data, allocated_date=form.allocated_date.data, vacated_date=form.vacated_date.data, status=form.status.data)
        db.session.add(ha)
        db.session.commit()
        flash('Room allocated to student!', 'success')
        return redirect(url_for('services_mgmt.list_hostel_allocations'))
    return render_template('crud/form.html', title='Allocate Room', form=form, back_url=url_for('services_mgmt.list_hostel_allocations'))

@services_mgmt_bp.route('/hostel/allocations/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_hostel_allocation(id):
    ha = HostelAllocation.query.get_or_404(id)
    form = HostelAllocationForm(obj=ha)
    form.room_id.choices = [(r.id, f"Room {r.room_number} (Bld {r.building_id})") for r in HostelRoom.query.all()]
    form.student_id.choices = [(s.id, f"{s.registration_number}") for s in Student.query.all()]
    if form.validate_on_submit():
        form.populate_obj(ha)
        db.session.commit()
        flash('Allocation updated!', 'success')
        return redirect(url_for('services_mgmt.list_hostel_allocations'))
    return render_template('crud/form.html', title='Edit Allocation', form=form, back_url=url_for('services_mgmt.list_hostel_allocations'))

@services_mgmt_bp.route('/hostel/allocations/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_hostel_allocation(id):
    ha = HostelAllocation.query.get_or_404(id)
    db.session.delete(ha)
    db.session.commit()
    flash('Allocation removed.', 'info')
    return redirect(url_for('services_mgmt.list_hostel_allocations'))


# ==================== TRANSPORT MODULE ====================
# 8. TRANSPORT ROUTES
@services_mgmt_bp.route('/transport/routes')
@login_required
def list_routes():
    routes = TransportRoute.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Bus Routes', items=routes,
                           columns=[('ID', 'id'), ('Route Name', 'route_name'), ('Start', 'start_point'), ('End', 'end_point'), ('Fare ($)', 'monthly_fare')],
                           create_url=url_for('services_mgmt.create_route'), edit_endpoint='services_mgmt.edit_route', delete_endpoint='services_mgmt.delete_route')

@services_mgmt_bp.route('/transport/routes/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_route():
    form = TransportRouteForm()
    if form.validate_on_submit():
        tr = TransportRoute(route_name=form.route_name.data, start_point=form.start_point.data, end_point=form.end_point.data, stops_description=form.stops_description.data, monthly_fare=form.monthly_fare.data)
        db.session.add(tr)
        db.session.commit()
        flash(f'Route "{tr.route_name}" created!', 'success')
        return redirect(url_for('services_mgmt.list_routes'))
    return render_template('crud/form.html', title='Add Bus Route', form=form, back_url=url_for('services_mgmt.list_routes'))

@services_mgmt_bp.route('/transport/routes/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_route(id):
    tr = TransportRoute.query.get_or_404(id)
    form = TransportRouteForm(obj=tr)
    if form.validate_on_submit():
        form.populate_obj(tr)
        db.session.commit()
        flash('Route updated!', 'success')
        return redirect(url_for('services_mgmt.list_routes'))
    return render_template('crud/form.html', title='Edit Route', form=form, back_url=url_for('services_mgmt.list_routes'))

@services_mgmt_bp.route('/transport/routes/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_route(id):
    tr = TransportRoute.query.get_or_404(id)
    db.session.delete(tr)
    db.session.commit()
    flash('Route deleted.', 'info')
    return redirect(url_for('services_mgmt.list_routes'))


# 9. TRANSPORT VEHICLES
@services_mgmt_bp.route('/transport/vehicles')
@login_required
def list_vehicles():
    vehicles = TransportVehicle.query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Fleet / Vehicles', items=vehicles,
                           columns=[('ID', 'id'), ('Plate #', 'vehicle_number'), ('Route ID', 'route_id'), ('Driver', 'driver_name'), ('Phone', 'driver_phone'), ('Status', 'status')],
                           create_url=url_for('services_mgmt.create_vehicle'), edit_endpoint='services_mgmt.edit_vehicle', delete_endpoint='services_mgmt.delete_vehicle')

@services_mgmt_bp.route('/transport/vehicles/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_vehicle():
    form = TransportVehicleForm()
    routes = [(0, '-- Unassigned Route --')] + [(r.id, r.route_name) for r in TransportRoute.query.all()]
    form.route_id.choices = routes
    if form.validate_on_submit():
        r_id = form.route_id.data if form.route_id.data != 0 else None
        tv = TransportVehicle(vehicle_number=form.vehicle_number.data.strip().upper(), route_id=r_id, capacity=form.capacity.data, driver_name=form.driver_name.data, driver_phone=form.driver_phone.data, status=form.status.data)
        db.session.add(tv)
        db.session.commit()
        flash('Vehicle registered successfully!', 'success')
        return redirect(url_for('services_mgmt.list_vehicles'))
    return render_template('crud/form.html', title='Add Fleet Vehicle', form=form, back_url=url_for('services_mgmt.list_vehicles'))

@services_mgmt_bp.route('/transport/vehicles/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_vehicle(id):
    tv = TransportVehicle.query.get_or_404(id)
    form = TransportVehicleForm(obj=tv)
    routes = [(0, '-- Unassigned Route --')] + [(r.id, r.route_name) for r in TransportRoute.query.all()]
    form.route_id.choices = routes
    if request.method == 'GET' and not tv.route_id:
        form.route_id.data = 0
    if form.validate_on_submit():
        form.populate_obj(tv)
        tv.vehicle_number = form.vehicle_number.data.strip().upper()
        tv.route_id = form.route_id.data if form.route_id.data != 0 else None
        db.session.commit()
        flash('Vehicle record updated!', 'success')
        return redirect(url_for('services_mgmt.list_vehicles'))
    return render_template('crud/form.html', title='Edit Vehicle', form=form, back_url=url_for('services_mgmt.list_vehicles'))

@services_mgmt_bp.route('/transport/vehicles/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_vehicle(id):
    tv = TransportVehicle.query.get_or_404(id)
    db.session.delete(tv)
    db.session.commit()
    flash('Vehicle removed.', 'info')
    return redirect(url_for('services_mgmt.list_vehicles'))


# 10. TRANSPORT ASSIGNMENTS
@services_mgmt_bp.route('/transport/assignments')
@login_required
def list_transport_assignments():
    query = TransportAssignment.query
    if current_user.has_role('STUDENT'):
        query = query.filter_by(user_id=current_user.id)
    assignments = query.paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Bus Pass Allocations', items=assignments,
                           columns=[('ID', 'id'), ('Vehicle ID', 'vehicle_id'), ('User ID', 'user_id'), ('Pickup Stop', 'pickup_stop'), ('Date', 'assigned_date'), ('Status', 'status')],
                           create_url=url_for('services_mgmt.create_transport_assignment'), edit_endpoint='services_mgmt.edit_transport_assignment', delete_endpoint='services_mgmt.delete_transport_assignment')

@services_mgmt_bp.route('/transport/assignments/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_transport_assignment():
    form = TransportAssignmentForm()
    form.vehicle_id.choices = [(v.id, f"{v.vehicle_number} (Driver: {v.driver_name})") for v in TransportVehicle.query.all()]
    form.user_id.choices = [(u.id, f"{u.full_name} ({u.email})") for u in User.query.all()]
    if form.validate_on_submit():
        ta = TransportAssignment(vehicle_id=form.vehicle_id.data, user_id=form.user_id.data, pickup_stop=form.pickup_stop.data, assigned_date=form.assigned_date.data, status=form.status.data)
        db.session.add(ta)
        db.session.commit()
        flash('Bus pass assigned!', 'success')
        return redirect(url_for('services_mgmt.list_transport_assignments'))
    return render_template('crud/form.html', title='Assign Bus Pass', form=form, back_url=url_for('services_mgmt.list_transport_assignments'))

@services_mgmt_bp.route('/transport/assignments/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_transport_assignment(id):
    ta = TransportAssignment.query.get_or_404(id)
    form = TransportAssignmentForm(obj=ta)
    form.vehicle_id.choices = [(v.id, f"{v.vehicle_number}") for v in TransportVehicle.query.all()]
    form.user_id.choices = [(u.id, f"{u.full_name}") for u in User.query.all()]
    if form.validate_on_submit():
        form.populate_obj(ta)
        db.session.commit()
        flash('Assignment updated!', 'success')
        return redirect(url_for('services_mgmt.list_transport_assignments'))
    return render_template('crud/form.html', title='Edit Assignment', form=form, back_url=url_for('services_mgmt.list_transport_assignments'))

@services_mgmt_bp.route('/transport/assignments/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_transport_assignment(id):
    ta = TransportAssignment.query.get_or_404(id)
    db.session.delete(ta)
    db.session.commit()
    flash('Assignment removed.', 'info')
    return redirect(url_for('services_mgmt.list_transport_assignments'))


# ==================== SYSTEM MODULE ====================
# 11. ANNOUNCEMENTS
@services_mgmt_bp.route('/announcements')
@login_required
def list_announcements():
    announcements = Announcement.query.order_by(Announcement.created_at.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='Campus Announcements', items=announcements,
                           columns=[('ID', 'id'), ('Title', 'title'), ('Target Audience', 'target_audience'), ('Published', 'is_published'), ('Date', 'created_at')],
                           create_url=url_for('services_mgmt.create_announcement'), edit_endpoint='services_mgmt.edit_announcement', delete_endpoint='services_mgmt.delete_announcement')

@services_mgmt_bp.route('/announcements/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_announcement():
    form = AnnouncementForm()
    if form.validate_on_submit():
        anc = Announcement(title=form.title.data, target_audience=form.target_audience.data, content=form.content.data, is_published=form.is_published.data, author_id=current_user.id)
        db.session.add(anc)
        db.session.commit()
        flash('Announcement posted!', 'success')
        return redirect(url_for('services_mgmt.list_announcements'))
    return render_template('crud/form.html', title='Post Announcement', form=form, back_url=url_for('services_mgmt.list_announcements'))

@services_mgmt_bp.route('/announcements/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_announcement(id):
    anc = Announcement.query.get_or_404(id)
    form = AnnouncementForm(obj=anc)
    if form.validate_on_submit():
        form.populate_obj(anc)
        db.session.commit()
        flash('Announcement updated!', 'success')
        return redirect(url_for('services_mgmt.list_announcements'))
    return render_template('crud/form.html', title='Edit Announcement', form=form, back_url=url_for('services_mgmt.list_announcements'))

@services_mgmt_bp.route('/announcements/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_announcement(id):
    anc = Announcement.query.get_or_404(id)
    db.session.delete(anc)
    db.session.commit()
    flash('Announcement deleted.', 'info')
    return redirect(url_for('services_mgmt.list_announcements'))


# 12. NOTIFICATIONS
@services_mgmt_bp.route('/notifications')
@login_required
def list_notifications():
    notifications = Notification.query.order_by(Notification.created_at.desc()).paginate(page=request.args.get('page', 1, type=int), per_page=10)
    return render_template('crud/list.html', title='System Notifications', items=notifications,
                           columns=[('ID', 'id'), ('User ID', 'user_id'), ('Title', 'title'), ('Is Read', 'is_read'), ('Created At', 'created_at')],
                           create_url=url_for('services_mgmt.create_notification'), edit_endpoint='services_mgmt.edit_notification', delete_endpoint='services_mgmt.delete_notification')

@services_mgmt_bp.route('/notifications/add', methods=['GET', 'POST'])
@login_required
@admin_required
def create_notification():
    form = NotificationForm()
    form.user_id.choices = [(u.id, f"{u.full_name} ({u.email})") for u in User.query.all()]
    if form.validate_on_submit():
        notif = Notification(user_id=form.user_id.data, title=form.title.data, message=form.message.data, is_read=form.is_read.data)
        db.session.add(notif)
        db.session.commit()
        flash('Notification dispatched!', 'success')
        return redirect(url_for('services_mgmt.list_notifications'))
    return render_template('crud/form.html', title='Send Notification', form=form, back_url=url_for('services_mgmt.list_notifications'))

@services_mgmt_bp.route('/notifications/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_notification(id):
    notif = Notification.query.get_or_404(id)
    form = NotificationForm(obj=notif)
    form.user_id.choices = [(u.id, f"{u.full_name} ({u.email})") for u in User.query.all()]
    if form.validate_on_submit():
        form.populate_obj(notif)
        db.session.commit()
        flash('Notification updated!', 'success')
        return redirect(url_for('services_mgmt.list_notifications'))
    return render_template('crud/form.html', title='Edit Notification', form=form, back_url=url_for('services_mgmt.list_notifications'))

@services_mgmt_bp.route('/notifications/<int:id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_notification(id):
    notif = Notification.query.get_or_404(id)
    db.session.delete(notif)
    db.session.commit()
    flash('Notification deleted.', 'info')
    return redirect(url_for('services_mgmt.list_notifications'))
