from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Book model
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    year_published = db.Column(db.Integer, nullable=False)
    book_type = db.Column(db.Integer, nullable=False)
    category = db.Column(db.String(50), nullable=False, default='General')
    active = db.Column(db.Boolean, default=True)
    available_copies = db.Column(db.Integer, nullable=False, default=1)
    description = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "author": self.author,
            "year_published": self.year_published,
            "book_type": self.book_type,
            "category": self.category,
            "active": self.active,
            "available_copies": self.available_copies,
            "description": self.description
        }

# Customer model
class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='active')
    registration_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    def can_borrow(self):
        from app import MAX_LOANS_PER_CUSTOMER
        active_loans = Loan.query.filter_by(cust_id=self.id, actual_return_date=None).count()
        return active_loans < MAX_LOANS_PER_CUSTOMER

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "age": self.age,
            "date_of_birth": str(self.date_of_birth),
            "email": self.email,
            "phone": self.phone,
            "status": self.status,
            "registration_date": str(self.registration_date)
        }

# Loan model
class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cust_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    loan_date = db.Column(db.Date, nullable=False)
    return_date = db.Column(db.Date, nullable=False)
    actual_return_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='ongoing')

    customer = db.relationship('Customer', backref=db.backref('loans', lazy=True))
    book = db.relationship('Book', backref=db.backref('loans', lazy=True))

    def is_overdue(self):
        if self.actual_return_date is None and self.return_date < datetime.utcnow().date():
            return True
        return False

    def to_dict(self):
        return {
            "id": self.id,
            "cust_id": self.cust_id,
            "book_id": self.book_id,
            "loan_date": str(self.loan_date),
            "return_date": str(self.return_date),
            "actual_return_date": str(self.actual_return_date) if self.actual_return_date else None,
            "status": self.status
        }

# Admin model
class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

   
    

# Notification model
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='new')
    priority = db.Column(db.String(10), nullable=False, default='medium')
    recipient_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
