import pytest
from app import app, db, Book, Customer, Loan, Admin, Notification

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use an in-memory database for testing
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()  # Create the tables in the in-memory database
        yield client
        db.session.remove()
        db.drop_all()

def test_home(client):
    response = client.get('/')
    assert response.status_code == 200
    assert response.json == {"message": "Welcome to the Library Management System!"}

def test_create_book(client):
    new_book = {
        "name": "Test Book",
        "author": "Author Name",
        "year_published": 2025,
        "book_type": "Fiction",
        "category": "Mystery",
        "description": "A thrilling mystery book."
    }
    response = client.post('/books', json=new_book)
    assert response.status_code == 201
    assert response.json['name'] == "Test Book"
    assert response.json['author'] == "Author Name"


def test_get_books(client):
    # First, add a book
    new_book = {
        "name": "Test Book 1",
        "author": "Author 1",
        "year_published": 2020,
        "book_type": "Fiction",
        "category": "Thriller",
        "description": "An exciting thriller."
    }
    client.post('/books', json=new_book)

    # Fetch all books
    response = client.get('/books')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['name'] == "Test Book 1"

def test_update_book(client):
    # Add a book
    new_book = {
        "name": "Original Book",
        "author": "Original Author",
        "year_published": 2015,
        "book_type": "Non-Fiction",
        "category": "History",
        "description": "A historical book."
    }
    response = client.post('/books', json=new_book)
    book_id = response.json['id']

    # Update the book
    updated_data = {
        "name": "Updated Book",
        "author": "Updated Author"
    }
    response = client.put(f'/books/{book_id}', json=updated_data)
    assert response.status_code == 200
    assert response.json['name'] == "Updated Book"
    assert response.json['author'] == "Updated Author"

def test_create_customer(client):
    # Create a new customer
    new_customer = {
        "name": "John Doe",
        "city": "New York",
        "age": 30,
        "date_of_birth": "1995-05-15",
        "email": "johndoe@example.com",
        "phone": "1234567890"
    }
    response = client.post('/customers', json=new_customer)
    assert response.status_code == 201
    assert response.json['name'] == "John Doe"
    assert response.json['email'] == "johndoe@example.com"

def test_get_customer(client):
    # Create a customer
    new_customer = {
        "name": "Jane Doe",
        "city": "Los Angeles",
        "age": 28,
        "date_of_birth": "1997-06-10",
        "email": "janedoe@example.com",
        "phone": "9876543210"
    }
    response = client.post('/customers', json=new_customer)
    customer_id = response.json['id']

    # Fetch the customer by ID
    response = client.get(f'/customers/{customer_id}')
    assert response.status_code == 200
    assert response.json['name'] == "Jane Doe"
    assert response.json['city'] == "Los Angeles"

def test_create_loan(client):
    # Add a customer and a book first
    customer = {
        "name": "Loan Customer",
        "city": "Chicago",
        "age": 35,
        "date_of_birth": "1988-01-01",
        "email": "loan.customer@example.com",
        "phone": "1234512345"
    }
    book = {
        "name": "Loan Book",
        "author": "Loan Author",
        "year_published": 2022,
        "book_type": "Fiction",
        "category": "Adventure",
        "description": "An adventure book."
    }
    customer_response = client.post('/customers', json=customer)
    book_response = client.post('/books', json=book)

    loan_data = {
        "cust_id": customer_response.json['id'],
        "book_id": book_response.json['id'],
        "loan_date": "2025-01-01",
        "return_date": "2025-01-15",
        "status": "ongoing"
    }
    response = client.post('/loans', json=loan_data)
    assert response.status_code == 201
    assert response.json['cust_id'] == customer_response.json['id']
    assert response.json['book_id'] == book_response.json['id']

def test_get_overdue_loans(client):
    # Add a customer, a book, and a loan with a past return date
    customer = {
        "name": "Overdue Customer",
        "city": "Boston",
        "age": 40,
        "date_of_birth": "1985-10-20",
        "email": "overdue@example.com",
        "phone": "5555555555"
    }
    book = {
        "name": "Overdue Book",
        "author": "Overdue Author",
        "year_published": 2020,
        "book_type": "Non-Fiction",
        "category": "Science",
        "description": "A science book."
    }
    customer_response = client.post('/customers', json=customer)
    book_response = client.post('/books', json=book)

    loan_data = {
        "cust_id": customer_response.json['id'],
        "book_id": book_response.json['id'],
        "loan_date": "2025-01-01",
        "return_date": "2025-01-10",  # Past date to make it overdue
        "status": "ongoing"
    }
    client.post('/loans', json=loan_data)

    # Get overdue loans
    response = client.get('/loans/overdue')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['cust_id'] == customer_response.json['id']

