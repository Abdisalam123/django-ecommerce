# EShopper

Full-featured Django e-commerce application demonstrating modern web development practices. Built with Django 4.x and Python 3.x for educational and portfolio purposes.

**⚠️ This is a demonstration project. Do not use for production without proper security hardening.**

## Features

- Full-featured product catalog with categories and search
- Session-based shopping cart with persistent state
- User authentication with guest checkout support
- Automated order processing and email confirmations
- Responsive web interface
- Admin panel for content management

## Quick Start

### Prerequisites

- Python 3.8+
- pip package manager
- Virtual environment (recommended)

### Installation

```bash
git clone https://github.com/Abdisalam123/django-ecommerce.git
cd django-ecommerce/eshopper
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Navigate to `http://127.0.0.1:8000` to access the application.

## Live Site

If you want to view the live site and test it you can access it here www.abdisalam.pythonanywhere.com

## Configuration

Most configuration options are available in `eshopper/settings.py`. Key settings include:

### Database
Default configuration uses SQLite. For production, configure PostgreSQL or MySQL:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Email Configuration
Configure SMTP settings for order confirmations:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.your-provider.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

### Media Files
Ensure media directory exists for product images:
```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

## Architecture

The application follows Django's Model-View-Template (MVT) pattern:

### Models (`store/models.py`)
- **Customer**: User accounts and authentication
- **Category**: Product categorization system
- **Product**: Product catalog with inventory tracking
- **Order**: Order management and status tracking
- **OrderItem**: Order line items (many-to-many through model)

### Views (`store/views.py`)
- Function-based views handling business logic
- Session management for cart and user state
- Form processing and validation
- Email integration for order confirmations

### Templates
- Responsive HTML templates using Django template engine
- Template inheritance for consistent layout
- Dynamic content rendering with context data

## API Endpoints

The application uses traditional Django URL patterns:

```
/                           # Home page with featured products
/product/<int:id>/          # Product detail page
/collections/<str:type>/    # Category product listings
/search/                    # Product search functionality
/cart/                      # Shopping cart interface
/login/                     # User authentication
/signup/                    # User registration
/orders/                    # Order history
/orders/<int:id>/           # Order details
```

## Development

### Setting up Development Environment

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Create superuser account
python manage.py createsuperuser

# Load sample data (optional)
python manage.py loaddata fixtures/sample_data.json

# Run development server with debug
python manage.py runserver --settings=eshopper.settings.dev
```

### Database Migrations

```bash
# Create new migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# View migration status
python manage.py showmigrations
```

### Testing

```bash
# Run test suite
python manage.py test

# Run specific test module
python manage.py test store.tests

# Generate coverage report
coverage run --source='.' manage.py test
coverage report
```

## Deployment

For production deployment, consider:

- Use environment variables for sensitive settings
- Configure proper database (PostgreSQL recommended)
- Set up static file serving (WhiteNoise or CDN)
- Implement proper logging and monitoring
- Enable HTTPS and security middleware
- Use WSGI server (Gunicorn, uWSGI)

Example production settings:
```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
```

## Performance Considerations

- Database queries use `select_related()` for foreign key optimization
- Session-based cart avoids database writes for guest users
- Product images are optimized for web delivery
- Consider implementing caching (Redis/Memcached) for production

## Security Features

- CSRF protection on all forms
- Password hashing using Django's built-in PBKDF2
- SQL injection prevention through Django ORM
- XSS protection via template auto-escaping
- Session security with secure cookie settings

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/enhancement`)
3. Follow existing code style and conventions
4. Add tests for new functionality
5. Submit a pull request with detailed description

## License

This project is provided for educational purposes. See LICENSE file for details.
