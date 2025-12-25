2Q@T# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Django-based budget tracking and cost accounting application, ported from VisualWorks Smalltalk 7.6. Provides comprehensive budget management with transaction tracking, import/export capabilities, cost accounting, and reporting features.

**Tech Stack:** Django 4.2+ / Python 3.13+ / PostgreSQL / Django REST Framework / Celery + Redis

## Development Commands

### Environment Setup

```bash
# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements-dev.txt

# Copy environment variables (then edit .env)
cp .env.example .env
```

### Database

```bash
# Run migrations
python manage.py migrate

# Create migrations after model changes
python manage.py makemigrations

# Create superuser
python manage.py createsuperuser
```

### Running the Application

```bash
# Development server
python manage.py runserver

# Django shell
python manage.py shell

# Access admin interface
# http://localhost:8000/admin
```

### Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest apps/budgets/tests/test_models.py

# Run specific test
pytest apps/budgets/tests/test_models.py::TestBudget::test_create_budget

# Run with coverage
pytest --cov=apps --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Code Quality

```bash
# Format code (before committing)
black .

# Check linting
flake8

# Type checking
mypy .

# Sort imports
isort .

# Run all quality checks
black . && isort . && flake8 && mypy .
```

## Architecture

### Core Domain Models

The application is structured around hierarchical budget management:

- **BudgetGroup**: Hierarchical containers for organizing budgets (tree structure)
- **Budget**: Main container for transactions; belongs to a BudgetGroup
- **BudgetItem**: Individual transactions (income/expenses) within a Budget
- **Category**: Classification for transactions (groceries, utilities, etc.)
- **AccountingCategory**: Cost accounting and IRS reporting categories
- **Member**: People/entities associated with transactions
- **Source**: Income sources
- **CategoryVendor**: Vendor tracking per category
- **BudgetItemRelation**: Links related transactions (parent/child breakouts)

### Critical Business Logic

**Running Balance Calculation:**
- Must be recalculated whenever transactions change
- Ordered by date and sequence number
- Each BudgetItem has a `running_balance` field that reflects balance after that transaction

**Transaction Breakouts:**
- Parent transactions can have child transactions that break down the total
- Children must sum to parent amount
- Parent value is automatically calculated from children
- Validation required to maintain consistency

**Import Duplicate Detection:**
- Matches on date, amount, and description
- Uses fuzzy matching logic
- User confirmation required for potential duplicates

**Budget Types:**
- Normal budgets: Standard budget tracking
- Copy budgets (`is_copy=True`): Backups/snapshots
- WhatIf budgets (`is_whatif=True`): Forecasting scenarios
- All relationships must be preserved when copying

### App Structure

```
apps/
├── core/          # Shared models (TimeStampedModel base class)
├── budgets/       # Core budget management (models, business logic)
├── imports/       # Import functionality (CSV, OFX/QFX, XML parsers)
├── exports/       # Export functionality (CSV, PDF, Excel)
├── reports/       # Reporting and analytics
├── lists/         # Auxiliary features (grocery lists, todo lists)
└── accounts/      # User authentication
```

### Import Parsers

Located in `apps/imports/parsers/`:
- `csv_parser.py`: CSV file imports
- `ofx_parser.py`: Bank statement imports (OFX/QFX format)
- `xml_parser.py`: Generic XML imports

All parsers must implement duplicate detection and return standardized data structures.

### Settings Organization

Settings are split by environment in `config/settings/`:
- `base.py`: Shared settings for all environments
- `development.py`: Local development (DEBUG=True, SQLite fallback)
- `test.py`: Test environment (in-memory DB, fast settings)
- `production.py`: Production settings (security hardened)

Default settings module: `config.settings.development`

## Database Schema Notes

### Key Fields

**BudgetItem unique_id format:** `{budget_id}_{sequence_number}` (ensures uniqueness across budgets)

**BudgetItem sequence_number:** Auto-incremented per budget (not globally); use `budget.get_next_sequence_number()`

**Indexes:** All models have appropriate indexes on foreign keys, search fields (name, date), and frequently filtered fields (is_copy, is_whatif)

### Model Relationships

- Budget → BudgetGroup (many-to-one)
- BudgetItem → Budget (many-to-one)
- BudgetItem → Category (many-to-one, PROTECT on delete)
- BudgetItem → Member, Source, CategoryVendor (optional, PROTECT/SET_NULL)
- BudgetItem → AccountingCategory (many-to-many)
- BudgetItemRelation: Links parent/child items for breakouts

## Testing Strategy

- Models: Test all business logic methods, validation, relationships
- Parsers: Test with sample files in repository (test_import.csv, test_bank_statement.ofx)
- Views/APIs: Test CRUD operations, permissions, error cases
- Target: 80% coverage minimum (configured in pyproject.toml)

Test factories are in `apps/budgets/tests/factories.py` - use these to create test data.

## Configuration

**Environment Variables:** See `.env.example` for all available options. Key variables:
- `ENVIRONMENT`: development/production/test
- `DB_*`: PostgreSQL credentials
- `SECRET_KEY`: Django secret (must change in production)

**Python Version:** 3.13+ (uses modern type hints and features)

**Database:** PostgreSQL 15+ recommended (SQLite fallback for development)

## Migration from Smalltalk

This project is migrating from a VisualWorks Smalltalk 7.6 application. Key context:

- Original business logic is proven and should be preserved
- Data migration scripts will be in `scripts/` directory
- Smalltalk naming conventions retained where sensible (e.g., `monitary_value` vs `monetary_value`)
- See `PROJECT_CONTEXT_SUMMARY.md` and `BUDGET_APP_ROADMAP.md` for full migration plan

## Development Workflow

1. **Before making model changes:** Consider impact on existing data
2. **After model changes:** Create migrations immediately (`makemigrations`)
3. **Before committing:** Run quality checks (`black . && isort . && flake8 && mypy .`)
4. **When adding features:** Write tests first or alongside implementation
5. **For imports/exports:** Test with real files (samples in repository root)

## Performance Considerations

- Use `select_related()` for foreign keys when querying BudgetItems
- Use `prefetch_related()` for many-to-many relationships (accounting_categories)
- Running balance recalculation can be expensive - use Celery tasks for bulk updates
- Database indexes are critical - already configured on high-traffic fields

## Common Patterns

**Creating a new BudgetItem:**
```python
sequence = budget.get_next_sequence_number()
item = BudgetItem.objects.create(
    budget=budget,
    sequence_number=sequence,
    unique_id=f"{budget.id}_{sequence}",
    date=transaction_date,
    monitary_value=amount,
    description=desc,
    category=category
)
```

**Querying with running balance:**
```python
items = BudgetItem.objects.filter(budget=budget).order_by('date', 'sequence_number')
```

**Recalculating running balances:**
Use the service in `apps/budgets/services/` (to be implemented) - never do manually in views.
source .venv/bin/activate