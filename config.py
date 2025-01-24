class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///library.db'  # Database URI
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'your_secret_key'
    
    # Email settings
    MAIL_SERVER = 'smtp.example.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your_email@example.com'
    MAIL_PASSWORD = 'your_password'
    
    # Max loans and other constants
    MAX_LOANS_PER_CUSTOMER = 2
    MAX_LOAN_DURATION = 14  # Max loan duration in days
