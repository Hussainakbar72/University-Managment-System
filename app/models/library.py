from datetime import datetime
from app.extensions import db

class LibraryBook(db.Model):
    __tablename__ = 'library_books'

    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(30), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    author = db.Column(db.String(150), nullable=False)
    publisher = db.Column(db.String(100), nullable=True)
    publication_year = db.Column(db.Integer, nullable=True)
    category = db.Column(db.String(80), nullable=False)  # Computer Science, AI, Mathematics, etc.

    copies = db.relationship('BookCopy', back_populates='book', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<LibraryBook {self.title} ({self.isbn})>"


class BookCopy(db.Model):
    __tablename__ = 'book_copies'

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('library_books.id', ondelete='CASCADE'), nullable=False, index=True)
    barcode = db.Column(db.String(50), unique=True, nullable=False, index=True)
    status = db.Column(db.String(20), default='Available', nullable=False)  # Available, Borrowed, Lost, Maintenance
    shelf_location = db.Column(db.String(50), nullable=False)

    book = db.relationship('LibraryBook', back_populates='copies')
    loans = db.relationship('LibraryLoan', back_populates='book_copy', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<BookCopy Barcode:{self.barcode} ({self.status})>"


class LibraryLoan(db.Model):
    __tablename__ = 'library_loans'

    id = db.Column(db.Integer, primary_key=True)
    book_copy_id = db.Column(db.Integer, db.ForeignKey('book_copies.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    borrow_date = db.Column(db.Date, default=datetime.utcnow, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), default='Active', nullable=False)  # Active, Returned, Overdue

    book_copy = db.relationship('BookCopy', back_populates='loans')
    user = db.relationship('User', back_populates='library_loans')
    fines = db.relationship('LibraryFine', back_populates='loan', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<LibraryLoan Copy:{self.book_copy_id} User:{self.user_id}>"


class LibraryFine(db.Model):
    __tablename__ = 'library_fines'

    id = db.Column(db.Integer, primary_key=True)
    loan_id = db.Column(db.Integer, db.ForeignKey('library_loans.id', ondelete='CASCADE'), nullable=False, index=True)
    amount = db.Column(db.Numeric(8, 2), nullable=False)
    status = db.Column(db.String(20), default='Unpaid', nullable=False)  # Unpaid, Paid, Waived
    paid_date = db.Column(db.DateTime, nullable=True)

    loan = db.relationship('LibraryLoan', back_populates='fines')

    def __repr__(self):
        return f"<LibraryFine Loan:{self.loan_id} Amount:{self.amount} ({self.status})>"
