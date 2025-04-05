# Smart Inventory Manager - AI-Powered Expiry Tracking

A modern Flask-based web application for intelligent inventory management and expiry date tracking. The system integrates with Zoho for inventory management and provides advanced features like OCR-based expiry date extraction, real-time notifications, and comprehensive analytics.

## 🌟 Key Features

- **Smart Inventory Management**
  - Real-time inventory tracking
  - Automated expiry date monitoring
  - Bulk operations support
  - Category-based organization

- **AI-Powered Features**
  - OCR-based expiry date extraction from images
  - Intelligent expiry predictions
  - Automated categorization

- **Integration Capabilities**
  - Seamless Zoho integration
  - Email notifications system
  - SMS alerts via Twilio (optional)
  - RESTful API support

- **Security & Compliance**
  - Secure user authentication
  - Role-based access control
  - Email verification
  - Password reset functionality

- **Analytics & Reporting**
  - Real-time dashboard
  - Customizable reports
  - Expiry trend analysis
  - Inventory insights

## 🚀 Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/smart-inventory-manager.git
cd smart-inventory-manager
```

2. **Set up the environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Configure the application**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Initialize the database**
```bash
flask db upgrade
```

5. **Run the application**
```bash
flask run
```

## 🔧 Configuration

The application is configured through environment variables in the `.env` file. See `.env.example` for all available options.

### Required Configuration
- Database URL
- Email settings
- Zoho credentials
- Secret key

### Optional Configuration
- Twilio settings for SMS
- Custom logging
- Session settings

## 📦 Project Structure

```
smart-inventory-manager/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # Application routes
│   ├── templates/       # HTML templates
│   ├── static/          # Static files
│   ├── tasks/           # Background tasks
│   └── utils/           # Utility functions
├── migrations/          # Database migrations
├── scripts/            # Utility scripts
├── tests/              # Test suite
└── docs/               # Documentation
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Flask Framework
- Zoho API
- Twilio API
- All contributors and supporters

## 📞 Support

For support, please open an issue in the GitHub repository or contact the maintainers.

## Features

- User authentication and authorization
- Inventory management with expiry date tracking
- OCR-based expiry date extraction from images
- Email and SMS notifications for expiring items
- Integration with Zoho for inventory sync
- Analytics and reporting
- Mobile-responsive design
- Scheduled tasks and background jobs
- Email notifications system

## Prerequisites

- Python 3.8 or higher
- PostgreSQL database
- Zoho account for inventory integration
- Twilio account for SMS notifications (optional)

## Configuration

The application can be configured through environment variables in the `.env` file:

- `FLASK_APP`: Application entry point
- `FLASK_ENV`: Environment (development/production)
- `DATABASE_URL`: PostgreSQL database URL
- `SECRET_KEY`: Application secret key
- `ZOHO_CLIENT_ID`: Zoho OAuth client ID
- `ZOHO_CLIENT_SECRET`: Zoho OAuth client secret
- `ZOHO_REDIRECT_URI`: Zoho OAuth redirect URI
- `TWILIO_ACCOUNT_SID`: Twilio account SID (optional)
- `TWILIO_AUTH_TOKEN`: Twilio auth token (optional)
- `TWILIO_PHONE_NUMBER`: Twilio phone number (optional)

## Usage

1. Start the development server:
```bash
flask run
```

2. Access the application at `http://localhost:5000`

3. Register a new account or log in with existing credentials

4. Connect your Zoho account for inventory sync

5. Start managing your inventory and tracking expiry dates

## Development

### Project Structure

```
project/
├── app/
│   ├── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   └── notification.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── products.py
│   │   └── notifications.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ocr_service.py
│   │   ├── zoho_service.py
│   │   └── notification_service.py
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   └── templates/
│       ├── base.html
│       ├── auth/
│       └── products/
├── config.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

### Running Tests

```bash
pytest
```

### Code Style

The project follows PEP 8 guidelines. Format code using:

```bash
black .
```

### Database Migrations

Create a new migration:
```bash
flask db migrate -m "description"
```

Apply migrations:
```bash
flask db upgrade
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Testing

The application uses pytest for testing. To run the tests:

```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
pytest

# Run specific test file
pytest tests/test_email_service.py

# Run tests with coverage report
pytest --cov=app tests/
```

## Utility Scripts

The `scripts` directory contains utility scripts for various tasks:

### Check Users
To view information about registered users:
```bash
python scripts/check_users.py
```

### Test Email
To test the email notification system:
```bash
python scripts/test_email.py
```

Note: Make sure your email configuration is properly set up in the `.env` file before running email-related scripts. 