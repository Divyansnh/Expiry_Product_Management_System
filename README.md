# Expiry Tracker

A comprehensive inventory management system with expiry date tracking, OCR capabilities, and automated notifications.

## Features

- Inventory management with expiry date tracking
- OCR-based expiry date extraction from images
- Email notifications for expiring items
- In-app notifications
- Daily status updates
- Integration with Zoho for inventory sync
- Analytics and reporting
- User authentication and authorization
- Responsive web interface

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript, Tailwind CSS
- **Database**: PostgreSQL
- **OCR**: Azure Computer Vision
- **Email**: SMTP (Gmail)
- **Authentication**: Flask-Login
- **API**: RESTful

## Prerequisites

- Python 3.8+
- PostgreSQL
- Azure Computer Vision account
- Gmail account for email notifications
- Zoho account for inventory integration (optional)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd expiry-tracker
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```
Edit `.env` with your configuration:
```env
# Flask Configuration
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/expiry_tracker

# Azure Computer Vision
AZURE_CV_KEY=your-azure-key
AZURE_CV_ENDPOINT=your-azure-endpoint

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Zoho Configuration (Optional)
ZOHO_CLIENT_ID=your-client-id
ZOHO_CLIENT_SECRET=your-client-secret
ZOHO_REDIRECT_URI=your-redirect-uri
```

5. Initialize the database:
```bash
flask db upgrade
```

## Usage

1. Start the development server:
```bash
flask run
```

2. Access the application at `http://localhost:5000`

3. Create an account and start managing your inventory

## Project Structure

```
expiry-tracker/
├── app/
│   ├── models/          # Database models
│   ├── routes/          # Route handlers
│   ├── services/        # Business logic
│   ├── templates/       # HTML templates
│   ├── static/          # Static files
│   └── core/            # Core functionality
├── scripts/             # Utility scripts
├── tests/               # Test files
├── migrations/          # Database migrations
├── .env                 # Environment variables
├── .gitignore          # Git ignore file
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask Framework
- Azure Computer Vision
- Zoho API
- All contributors and supporters 