from datetime import datetime
from app.extensions import db

class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    target_audience = db.Column(db.String(50), default='All', nullable=False)  # All, Students, Instructors, Staff
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_published = db.Column(db.Boolean, default=True, nullable=False)

    author = db.relationship('User', back_populates='announcements')

    def __repr__(self):
        return f"<Announcement {self.title} (Audience: {self.target_audience})>"


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    user = db.relationship('User', back_populates='notifications')

    def __repr__(self):
        return f"<Notification User:{self.user_id} Read:{self.is_read}>"


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    action = db.Column(db.String(100), nullable=False)  # CREATE_COURSE, DELETE_STUDENT, UPDATE_GRADE, etc.
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    details = db.Column(db.Text, nullable=True)

    user = db.relationship('User', back_populates='audit_logs')

    def __repr__(self):
        return f"<AuditLog {self.action} on {self.table_name}:{self.record_id}>"
