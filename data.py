from datetime import datetime, date
from app import app, db
from models import Admin, Book, Customer, Loan, Notification
from werkzeug.security import generate_password_hash

# Ensure the seeding process is inside the application context
with app.app_context():
    # Create tables
    db.create_all()

    # Add books
    book1 = Book(name='The Great Gatsby', author='F. Scott Fitzgerald', year_published=1925, book_type=1, category='Fiction', available_copies=5)
    book2 = Book(name='To Kill a Mockingbird', author='Harper Lee', year_published=1960, book_type=1, category='Fiction', available_copies=3)
    book3 = Book(name='1984', author='George Orwell', year_published=1949, book_type=1, category='Fiction', available_copies=4)
    book4 = Book(name='The Catcher in the Rye', author='J.D. Salinger', year_published=1951, book_type=1, category='Fiction', available_copies=2)
    book5 = Book(name='The Hobbit', author='J.R.R. Tolkien', year_published=1937, book_type=2, category='Fantasy', available_copies=3)
    book6 = Book(name='The Lord of the Rings', author='J.R.R. Tolkien', year_published=1954, book_type=2, category='Fantasy', available_copies=2)
    book7 = Book(name='The Da Vinci Code', author='Dan Brown', year_published=2003, book_type=3, category='Mystery', available_copies=3)
    book8 = Book(name='Angels & Demons', author='Dan Brown', year_published=2000, book_type=3, category='Mystery', available_copies=2)
    book9 = Book(name='The Lost Symbol', author='Dan Brown', year_published=2009, book_type=3, category='Mystery', available_copies=3)
    book10 = Book(name='Inferno', author='Dan Brown', year_published=2013, book_type=3, category='Mystery', available_copies=2)
    db.session.add_all([book1, book2, book3, book4, book5, book6, book7, book8, book9, book10])

    # Add customers
    customer1 = Customer(name='Alice', city='New York', age=25, date_of_birth=date(1995, 1, 15), email='alice@example.com', phone='1234567890')
    customer2 = Customer(name='Bob', city='Los Angeles', age=30, date_of_birth=date(1990, 5, 20), email='bob@example.com', phone='0987654321')
    customer3 = Customer(name='Charlie', city='Chicago', age=35, date_of_birth=date(1985, 10, 25), email='charlie@example.com', phone='1122334455')
    customer4 = Customer(name='David', city='Houston', age=40, date_of_birth=date(1980, 3, 30), email='david@example.com', phone='5566778899')
    customer5 = Customer(name='Eve', city='Phoenix', age=45, date_of_birth=date(1975, 8, 5), email='eve@example.com', phone='6677889900')
    db.session.add_all([customer1, customer2, customer3, customer4, customer5])

    # Add loans
    loan1 = Loan(book_id=1, cust_id=1, loan_date=date(2021, 3, 1), return_date=date(2021, 3, 15))
    loan2 = Loan(book_id=2, cust_id=2, loan_date=date(2021, 3, 2), return_date=date(2021, 3, 16))
    loan3 = Loan(book_id=3, cust_id=3, loan_date=date(2021, 3, 3), return_date=date(2021, 3, 17))
    loan4 = Loan(book_id=4, cust_id=4, loan_date=date(2021, 3, 4), return_date=date(2021, 3, 18))
    loan5 = Loan(book_id=5, cust_id=5, loan_date=date(2021, 3, 5), return_date=date(2021, 3, 19))
    db.session.add_all([loan1, loan2, loan3, loan4, loan5])

    # Add admin
    admin1 = Admin(username='admin', password=generate_password_hash('123', method='pbkdf2:sha256'))
    db.session.add(admin1)

    #add notifications
    notification1 = Notification(message='Book The Great Gatsby is due for return on 2021-03-15', cust_id=1)
    notification2 = Notification(message='Book To Kill a Mockingbird is due for return on 2021-03-16', cust_id=2)
    notification3 = Notification(message='Book 1984 is due for return on 2021-03-17', cust_id=3)
    notification4 = Notification(message='Book The Catcher in the Rye is due for return on 2021-03-18', cust_id=4)
    notification5 = Notification(message='Book The Hobbit is due for return on 2021-03-19', cust_id=5)
    db.session.add_all([notification1, notification2, notification3, notification4, notification5])
    def update_notification_status(notification_id):
        with app.app_context():
            # Get the notification by ID
            notification = Notification.query.get(notification_id)
            
            if notification:
                # Update its status to 'read'
                notification.status = 'read'
                
                # Commit the update to the database
                db.session.commit()
                
                print('Notification status updated successfully.')
            else:
                print('Notification not found.')

# Example: Update notification with ID 1
update_notification_status(1)

    # Commit all changes
db.session.commit()

print('Data seeded successfully!')

# Entry point to run the application
if __name__ == '__main__':
    app.run(debug=True)

