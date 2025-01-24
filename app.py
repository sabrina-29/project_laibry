from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_login import LoginManager, login_user, login_required, logout_user
from datetime import datetime
from models import db, Book, Customer, Loan, Admin, Notification
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
mail = Mail(app)


@app.route('/', methods=['GET'])
def home():
    return jsonify({"message": "Welcome to the Library Management System!"})

# Book CRUD Routes

# Create a new book
@app.route('/books', methods=['POST'])
def create_book():
    data = request.get_json()
    book = Book(
        name=data.get('name'),
        author=data.get('author'),
        year_published=data.get('year_published'),
        book_type=data.get('book_type'),
        category=data.get('category'),
        description=data.get('description'),
    )
    db.session.add(book)
    db.session.commit()
    return jsonify(book.to_dict()), 201

# Get all active books
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.filter_by(active=True).all()
    return jsonify([book.to_dict() for book in books])

# Get a specific active book by ID
@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    book = Book.query.get(id)
    if book and book.active:
        return jsonify(book.to_dict())
    return jsonify({"error": "Book not found"}), 404

# Update a specific book by ID
@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    data = request.get_json()
    book = Book.query.get(id)
    if book:
        book.name = data.get('name', book.name)
        book.author = data.get('author', book.author)
        book.year_published = data.get('year_published', book.year_published)
        book.book_type = data.get('book_type', book.book_type)
        book.category = data.get('category', book.category)
        book.description = data.get('description', book.description)
        db.session.commit()
        return jsonify(book.to_dict())
    return jsonify({"error": "Book not found"}), 404

# Deactivate a book (make it inactive)
@app.route('/books/<int:id>/deactivate', methods=['PATCH'])
def deactivate_book(id):
    book = Book.query.get(id)
    if book:
        book.active = False
        db.session.commit()
        return jsonify({"message": "Book deactivated successfully"}), 200
    return jsonify({"error": "Book not found"}), 404



# Create Customer
@app.route('/customers', methods=['POST'])
def create_customer():
    data = request.get_json()

    try:
        new_customer = Customer(
            name=data['name'],
            city=data['city'],
            age=data['age'],
            date_of_birth=data['date_of_birth'],
            email=data['email'],
            phone=data['phone'],
            status=data.get('status', 'active')
        )

        db.session.add(new_customer)
        db.session.commit()
        return jsonify(new_customer.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Get Customer by ID
@app.route('/customers/<int:id>', methods=['GET'])
def get_customer(id):
    customer = Customer.query.get_or_404(id)
    return jsonify(customer.to_dict())

# Update Customer
@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    data = request.get_json()
    customer = Customer.query.get_or_404(id)

    try:
        customer.name = data.get('name', customer.name)
        customer.city = data.get('city', customer.city)
        customer.age = data.get('age', customer.age)
        customer.date_of_birth = data.get('date_of_birth', customer.date_of_birth)
        customer.email = data.get('email', customer.email)
        customer.phone = data.get('phone', customer.phone)
        customer.status = data.get('status', customer.status)

        db.session.commit()
        return jsonify(customer.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# Mark Customer as Inactive (instead of delete)
@app.route('/customers/<int:id>', methods=['DELETE'])
def deactivate_customer(id):
    customer = Customer.query.get_or_404(id)
    
    try:
        customer.status = 'inactive'
        db.session.commit()
        return jsonify({'message': 'Customer marked as inactive'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

# List All Customers (Optional)
@app.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    return jsonify([customer.to_dict() for customer in customers])

#Activate Customer
@app.route('/customers/<int:id>/activate', methods=['PATCH'])
def activate_customer(id):
    customer = Customer.query.get_or_404(id)
    
    try:
        customer.status = 'active'
        db.session.commit()
        return jsonify({'message': 'Customer reactivated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

#Get All Inactive Customers
@app.route('/customers/inactive', methods=['GET'])
def get_inactive_customers():
    inactive_customers = Customer.query.filter_by(status='inactive').all()
    return jsonify([customer.to_dict() for customer in inactive_customers])

#Bulk Update Customer Status
@app.route('/customers/bulk_update_status', methods=['POST'])
def bulk_update_status():
    data = request.get_json()
    customer_ids = data.get('customer_ids', [])
    new_status = data.get('status', 'inactive')
    
    try:
        customers = Customer.query.filter(Customer.id.in_(customer_ids)).all()
        for customer in customers:
            customer.status = new_status
        db.session.commit()
        return jsonify({'message': f'{len(customers)} customers updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

#Get Customer Loan Information 
@app.route('/customers/<int:id>/loans', methods=['GET'])
def get_customer_loans(id):
    customer = Customer.query.get_or_404(id)
    loans = Loan.query.filter_by(cust_id=customer.id).all()
    return jsonify([loan.to_dict() for loan in loans])


# Create a new loan

@app.route('/loans', methods=['POST'])
def create_loan():
    data = request.get_json()
    # Validate if customer and book exist
    customer = Customer.query.get(data['cust_id'])
    book = Book.query.get(data['book_id'])

    if not customer:
        return jsonify({"message": "Customer not found"}), 404
    if not book:
        return jsonify({"message": "Book not found"}), 404

    new_loan = Loan(
        cust_id=data['cust_id'],
        book_id=data['book_id'],
        loan_date=datetime.strptime(data['loan_date'], '%Y-%m-%d').date(),
        return_date=datetime.strptime(data['return_date'], '%Y-%m-%d').date(),
        status=data.get('status', 'ongoing')
    )
    db.session.add(new_loan)
    db.session.commit()
    return jsonify(new_loan.to_dict()), 201

    data = request.get_json()
    new_loan = Loan(
        cust_id=data['cust_id'],
        book_id=data['book_id'],
        loan_date=datetime.strptime(data['loan_date'], '%Y-%m-%d').date(),
        return_date=datetime.strptime(data['return_date'], '%Y-%m-%d').date(),
        status=data.get('status', 'ongoing')
    )
    db.session.add(new_loan)
    db.session.commit()
    return jsonify(new_loan.to_dict()), 201

# Get all loans
@app.route('/loans', methods=['GET'])
def get_loans():
    loans = Loan.query.all()
    return jsonify([loan.to_dict() for loan in loans])

# Get a specific loan by ID
@app.route('/loans/<int:id>', methods=['GET'])
def get_loan(id):
    loan = Loan.query.get_or_404(id)
    return jsonify(loan.to_dict())

# Update a loan (e.g., update return date or status)
@app.route('/loans/<int:id>', methods=['PUT'])
def update_loan(id):
    data = request.get_json()
    loan = Loan.query.get_or_404(id)

    if 'status' in data:
        loan.status = data['status']
    if 'actual_return_date' in data:
        loan.actual_return_date = datetime.strptime(data['actual_return_date'], '%Y-%m-%d').date()

    db.session.commit()
    return jsonify(loan.to_dict())

# Delete a loan
@app.route('/loans/<int:id>', methods=['DELETE'])
def delete_loan(id):
    loan = Loan.query.get_or_404(id)
    db.session.delete(loan)
    db.session.commit()
    return '', 204

# Get all overdue loans
@app.route('/loans/overdue', methods=['GET'])
def overdue_loans():
    overdue_loans = Loan.query.filter(
        Loan.status == 'ongoing', 
        Loan.return_date < datetime.utcnow().date()
    ).all()
    return jsonify([loan.to_dict() for loan in overdue_loans])

# Notify customers with overdue loans
@app.route('/loans/overdue/notify', methods=['GET'])
def notify_overdue_loans():
    overdue_loans = Loan.query.filter(
        Loan.status == 'ongoing', 
        Loan.return_date < datetime.utcnow().date()
    ).all()
    overdue_customers = []
    
    for loan in overdue_loans:
        customer = loan.customer
        overdue_customers.append({
            'customer_name': customer.name,
            'email': customer.email,
            'book_title': loan.book.title,
            'due_date': loan.return_date
        })

    # Here you would integrate email-sending logic
    # For example, call a function like send_overdue_notifications(overdue_customers)
    return jsonify(overdue_customers), 200


# Create Admin
@app.route('/admin', methods=['POST'])
def create_admin():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    hashed_password = generate_password_hash(password, method='sha256')

    new_admin = Admin(username=username, password=hashed_password)
    db.session.add(new_admin)
    db.session.commit()

    return jsonify({'message': 'Admin created successfully'}), 201

# Read Admin by ID
@app.route('/admin/<int:id>', methods=['GET'])
@login_required
def get_admin(id):
    admin = Admin.query.get_or_404(id)
    return jsonify({'id': admin.id, 'username': admin.username}), 200

# Update Admin
@app.route('/admin/<int:id>', methods=['PUT'])
@login_required
def update_admin(id):
    data = request.get_json()
    admin = Admin.query.get(id)
    if not admin:
        return jsonify({'message': 'Admin not found'}), 404

    admin.username = data.get('username', admin.username)
    if 'password' in data:
        admin.password = generate_password_hash(data.get('password'))

    db.session.commit()
    return jsonify({'message': 'Admin updated successfully'}), 200

# Delete Admin
@app.route('/admin/<int:id>', methods=['DELETE'])
@login_required
def delete_admin(id):
    admin = Admin.query.get(id)
    if not admin:
        return jsonify({'message': 'Admin not found'}), 404

    db.session.delete(admin)
    db.session.commit()
    return jsonify({'message': 'Admin deleted successfully'}), 200

# Login Route (for Admin)
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    admin = Admin.query.filter_by(username=username).first()
    if admin and check_password_hash(admin.password, password):
        login_user(admin)
        return jsonify({'message': 'Login successful'}), 200
    return jsonify({'message': 'Invalid username or password'}), 401

# Logout Route
@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'}), 200


# Create a notification
@app.route('/notifications', methods=['POST'])
def create_notification():
    data = request.get_json()
    new_notification = Notification(
        type=data['type'],
        content=data['content'],
        status=data.get('status', 'new'),
        priority=data['priority'],
        recipient_id=data.get('recipient_id'),
    )
    db.session.add(new_notification)
    db.session.commit()
    return jsonify({'message': 'Notification created', 'id': new_notification.id}), 201

# Read all notifications
@app.route('/notifications', methods=['GET'])
def get_notifications():
    notifications = Notification.query.all()
    result = []
    for notification in notifications:
        result.append({
            'id': notification.id,
            'type': notification.type,
            'content': notification.content,
            'status': notification.status,
            'priority': notification.priority,
            'recipient_id': notification.recipient_id,
            'created_at': notification.created_at,
        })
    return jsonify(result)

# Read a specific notification by ID
@app.route('/notifications/<int:id>', methods=['GET'])
def get_notification(id):
    notification = Notification.query.get_or_404(id)
    return jsonify({
        'id': notification.id,
        'type': notification.type,
        'content': notification.content,
        'status': notification.status,
        'priority': notification.priority,
        'recipient_id': notification.recipient_id,
        'created_at': notification.created_at,
    })

# Update a notification
@app.route('/notifications/<int:id>', methods=['PUT'])
def update_notification(id):
    notification = Notification.query.get_or_404(id)
    data = request.get_json()

    notification.type = data.get('type', notification.type)
    notification.content = data.get('content', notification.content)
    notification.status = data.get('status', notification.status)
    notification.priority = data.get('priority', notification.priority)
    notification.recipient_id = data.get('recipient_id', notification.recipient_id)

    db.session.commit()
    return jsonify({'message': 'Notification updated'})

# Delete a notification
@app.route('/notifications/<int:id>', methods=['DELETE'])
def delete_notification(id):
    notification = Notification.query.get_or_404(id)
    db.session.delete(notification)
    db.session.commit()
    return jsonify({'message': 'Notification deleted'})


@app.route('/update_notification_status/<int:notification_id>', methods=['PATCH'])
def update_notification_status(notification_id):
    with app.app_context():
        # Get the notification by ID
        notification = Notification.query.get(notification_id)
        
        if notification:
            # Update its status to 'read'
            notification.status = 'read'
            
            # Commit the update to the database
            db.session.commit()
            
            return jsonify({"message": "Notification status updated successfully."}), 200
        else:
            return jsonify({"message": "Notification not found."}), 404

if __name__ == "__main__":
    app.run(debug=True)
