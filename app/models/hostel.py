from datetime import datetime
from app.extensions import db

class HostelBuilding(db.Model):
    __tablename__ = 'hostel_buildings'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    campus_id = db.Column(db.Integer, db.ForeignKey('campuses.id', ondelete='CASCADE'), nullable=False, index=True)
    gender_type = db.Column(db.String(20), nullable=False)  # Male, Female, Mixed
    warden_name = db.Column(db.String(120), nullable=True)
    total_floors = db.Column(db.Integer, default=3, nullable=False)

    campus = db.relationship('Campus', back_populates='hostel_buildings')
    rooms = db.relationship('HostelRoom', back_populates='building', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<HostelBuilding {self.name}>"


class HostelRoom(db.Model):
    __tablename__ = 'hostel_rooms'

    id = db.Column(db.Integer, primary_key=True)
    building_id = db.Column(db.Integer, db.ForeignKey('hostel_buildings.id', ondelete='CASCADE'), nullable=False, index=True)
    room_number = db.Column(db.String(30), nullable=False)
    capacity = db.Column(db.Integer, default=2, nullable=False)
    monthly_fee = db.Column(db.Numeric(10, 2), nullable=False)
    room_type = db.Column(db.String(50), default='Standard', nullable=False)  # Standard, Deluxe, Cubicle

    building = db.relationship('HostelBuilding', back_populates='rooms')
    allocations = db.relationship('HostelAllocation', back_populates='room', cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('building_id', 'room_number', name='uq_building_room'),
    )

    def __repr__(self):
        return f"<HostelRoom {self.room_number} (Building {self.building_id})>"


class HostelAllocation(db.Model):
    __tablename__ = 'hostel_allocations'

    id = db.Column(db.Integer, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('hostel_rooms.id', ondelete='CASCADE'), nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False, index=True)
    allocated_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    vacated_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='Active', nullable=False)  # Active, Vacated, Suspended

    room = db.relationship('HostelRoom', back_populates='allocations')
    student = db.relationship('Student', back_populates='hostel_allocations')

    def __repr__(self):
        return f"<HostelAllocation Room:{self.room_id} Student:{self.student_id}>"
