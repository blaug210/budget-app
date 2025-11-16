# Budget Application

A modern Django-based budget tracking and cost accounting application, ported from VisualWorks Smalltalk 7.6.

## Project Overview

This application provides comprehensive budget management with features including:

- Hierarchical budget groups and budgets
- Transaction tracking with running balances
- Import/export (CSV, OFX/QFX, Quicken, Excel, PDF)
- Cost accounting and IRS reporting
- Advanced filtering and search
- Transaction breakouts and relations
- Reporting and analytics

## Tech Stack

- **Backend:** Django 4.2+ / Python 3.13+
- **Database:** PostgreSQL 15+
- **API:** Django REST Framework
- **Task Queue:** Celery + Redis
- **Frontend:** TBD (React or Django Templates)

## Getting Started

### Prerequisites

- Python 3.13+
- PostgreSQL 15+
- Redis (for Celery)

### Installation

1. **Clone the repository:**
   ```bash
   git clone git@github.com:blaug210/budget-app.git
   cd budget-app
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3.13 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and other settings
   ```

5. **Set up PostgreSQL database:**
   ```bash
   createdb budget_app_dev
   createuser budget_user
   # Set password and grant privileges
   ```

6. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

7. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

8. **Run development server:**
   ```bash
   python manage.py runserver
   ```

Visit http://localhost:8000/admin to access the Django admin interface.

## Project Structure

```
budget_app/
├── apps/                    # Django applications
│   ├── budgets/            # Budget management
│   ├── imports/            # Import functionality
│   ├── exports/            # Export functionality
│   ├── reports/            # Reporting and analytics
│   ├── lists/              # Grocery/todo lists
│   └── accounts/           # User authentication
├── config/                 # Django settings
│   └── settings/           # Environment-specific settings
├── static/                 # Static files
├── media/                  # User uploads
├── templates/              # Django templates
├── scripts/                # Utility scripts
└── docs/                   # Documentation
```

## Development

### Running Tests

```bash
pytest
```

### Code Quality

```bash
# Format code
black .

# Lint code
flake8

# Type checking
mypy .

# Sort imports
isort .
```

### Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

## Environment Variables

See `.env.example` for all available configuration options.

Key variables:
- `ENVIRONMENT`: development, production, or test
- `DEBUG`: Enable/disable debug mode
- `SECRET_KEY`: Django secret key (change in production!)
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Database credentials

## Documentation

- [Roadmap](BUDGET_APP_ROADMAP.md) - Complete development plan
- [Context Summary](PROJECT_CONTEXT_SUMMARY.md) - Project background and context

## Development Status

**Phase 1: Foundation & Architecture** (In Progress)
- [x] Week 1: Project Setup
- [ ] Week 2: Database Design
- [ ] Week 3: Core Infrastructure

See [BUDGET_APP_ROADMAP.md](BUDGET_APP_ROADMAP.md) for the complete development timeline.

## Contributing

This is currently a personal project, but contributions may be welcome in the future.

## License

TBD

## Contact

For questions or issues, please open an issue on GitHub.
