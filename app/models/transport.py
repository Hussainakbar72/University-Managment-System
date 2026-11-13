from datetime import datetime
from app.extensions import db

class TransportRoute(db.Model):
    __tablename__ = 'transport_routes'

    id = db.Column(db.Integer, primary_key=True)
    route_name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    start_point = db.Column(db.String(120), nullable=False)
    end_point = db.Column(db.String(120), nullable=False)
    stops_description = db.Column(db.Text, nullable=True)
    monthly_fare = db.Column(db.Numeric(10, 2), nullable=False)

    vehicles = db.relationship('TransportVehicle', back_populates='route', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<TransportRoute {self.route_name}>"


class TransportVehicle(db.Model):
    __tablename__ = 'transport_vehicles'

    id = db.Column(db.Integer, primary_key=True)
    vehicle_number = db.Column(db.String(30), unique=True, nullable=False, index=True)
    route_id = db.Column(db.Integer, db.ForeignKey('transport_routes.id', ondelete='SET NULL'), nullable=True, index=True)
    capacity = db.Column(db.Integer, nullable=False)
    driver_name = db.Column(db.String(100), nullable=False)
    driver_phone = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(20), default='Active', nullable=False)  # Active, Maintenance, Out of Service

    route = db.relationship('TransportRoute', back_populates='vehicles')
    assignments = db.relationship('TransportAssignment', back_populates='vehicle', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<TransportVehicle {self.vehicle_number} (Driver: {self.driver_name})>"


class TransportAssignment(db.Model):
    __tablename__ = 'transport_assignments'

    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('transport_vehicles.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    assigned_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    pickup_stop = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(20), default='Active', nullable=False)  # Active, Cancelled

    vehicle = db.relationship('TransportVehicle', back_populates='assignments')
    user = db.relationship('User', back_populates='transport_assignments')

    __table_args__ = (
        db.UniqueConstraint('vehicle_id', 'user_id', name='uq_vehicle_user_assignment'),
    )

    def __repr__(self):
        return f"<TransportAssignment Vehicle:{self.vehicle_id} User:{self.user_id}>"
