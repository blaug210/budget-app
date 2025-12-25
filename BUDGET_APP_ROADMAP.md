# Budget Application - Smalltalk to Django/Python Port

## Project Overview

This document outlines the complete roadmap for porting a VisualWorks Smalltalk 7.6 budget tracking and cost accounting application to a modern Python Django web application.

### Source System
- **Platform:** VisualWorks Smalltalk 7.6 NonCommercial
- **Source Location:** `I:\Geek Squad Data Backup 2025-01-14\from 2TB WD Green\Hdrive\Cincom_old\image`
- **Main Image:** `budget_visualnc.07.01.5 - Copy - back - Test.2.007 - Copy - Copy.1.1.1.1.bak.im`
- **Database:** PostgreSQL integration already exists
- **Namespace:** `Blau2102.Budget`

### Target System
- **Framework:** Django 4.2+
- **Database:** PostgreSQL
- **Frontend:** React or Django Templates (to be decided)
- **Deployment:** Docker + Docker Compose

---

## Application Features

### Core Functionality
The Smalltalk application provides:

1. **Budget Management**
   - Hierarchical budget groups and budgets
   - Transaction tracking (budget items)
   - Running balance calculations
   - Budget copying and "what-if" scenarios
   - Multi-budget management with tree view

2. **Transaction Management**
   - Budget items with:
     - Monetary values (income/expenses)
     - Dates (entry date, posted date)
     - Descriptions
     - Categories
     - Accounting categories (for cost accounting/IRS)
     - Members (people/entities)
     - Sources (income sources)
     - Vendors (CategoryVendor)
     - Reference numbers
     - Unique IDs
     - Running balance
     - Import source tracking

3. **Data Import/Export**
   - CSV import/export
   - Bank statement import (OFX/QFX)
   - Quicken data import
   - Duplicate detection
   - Import tracking
   - Text file export
   - Fixed distribution handling (e.g., Kohl's Fixed Distribution)

4. **Organization**
   - Categories for expense/income classification
   - Accounting categories for cost accounting
   - Members for tracking who spent/received money
   - Sources for income tracking
   - Budget groups for hierarchical organization

5. **Advanced Features**
   - Transaction relationships (linked items)
   - Breakouts (splitting transactions)
   - Multi-key filtering (dates, categories, members, amounts)
   - Notes system (per budget, per group, application-level)
   - Search across budgets
   - Backup/archive functionality

6. **Auxiliary Features**
   - Grocery list management
   - Todo list functionality
   - Shopping lists

---

## Technology Stack

### Backend
```
django==4.2.*
djangorestframework==3.14.*
psycopg2-binary==2.9.*
django-cors-headers==4.3.*
celery==5.3.*  # For background tasks
redis==5.0.*   # For Celery broker
python-dateutil==2.8.*
pytz==2024.*
```

### Data Processing
```
pandas==2.0.*
numpy==1.24.*
ofxparse==0.21  # Bank statement parsing
openpyxl==3.1.*  # Excel export
xlrd==2.0.*      # Excel import
reportlab==4.0.* # PDF generation
```

### Development & Testing
```
pytest==7.4.*
pytest-django==4.5.*
pytest-cov==4.1.*
factory-boy==3.3.*  # Test fixtures
faker==20.1.*       # Test data
black==24.*         # Code formatting
flake8==7.*         # Linting
mypy==1.8.*         # Type checking
```

### Frontend (Option 1: React)
```
React 18+
Axios for API calls
React Router
Material-UI or Ant Design
Chart.js or Recharts for visualizations
```

### Frontend (Option 2: Django Templates)
```
Django templates
Bootstrap 5
HTMX for dynamic updates
Chart.js for visualizations
```

### Deployment
```
docker==24.*
docker-compose
gunicorn==21.*
nginx
PostgreSQL 15+
```

---

## Project Structure

```
budget_app/
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── .gitignore
├── manage.py
├── pytest.ini
├── setup.cfg
│
├── config/                      # Django project settings
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py             # Base settings
│   │   ├── development.py      # Dev settings
│   │   ├── production.py       # Prod settings
│   │   └── test.py             # Test settings
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                        # Django apps
│   ├── __init__.py
│   │
│   ├── core/                   # Core models and utilities
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── managers.py
│   │   ├── mixins.py
│   │   └── utils.py
│   │
│   ├── budgets/                # Budget management
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── budget.py
│   │   │   ├── budget_item.py
│   │   │   ├── category.py
│   │   │   ├── accounting_category.py
│   │   │   ├── member.py
│   │   │   ├── source.py
│   │   │   ├── vendor.py
│   │   │   ├── budget_group.py
│   │   │   └── budget_item_relation.py
│   │   ├── views.py
│   │   ├── serializers.py      # DRF serializers
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── budget_service.py
│   │   │   ├── transaction_service.py
│   │   │   ├── balance_calculator.py
│   │   │   └── filter_service.py
│   │   ├── tasks.py            # Celery tasks
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       ├── test_views.py
│   │       ├── test_services.py
│   │       └── factories.py
│   │
│   ├── imports/                # Import functionality
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── import_tracker.py
│   │   │   └── import_log.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── csv_importer.py
│   │   │   ├── ofx_importer.py
│   │   │   ├── quicken_importer.py
│   │   │   └── duplicate_detector.py
│   │   ├── parsers/
│   │   │   ├── __init__.py
│   │   │   ├── csv_parser.py
│   │   │   ├── ofx_parser.py
│   │   │   └── base_parser.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── tests/
│   │
│   ├── exports/                # Export functionality
│   │   ├── __init__.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── csv_exporter.py
│   │   │   ├── excel_exporter.py
│   │   │   ├── pdf_exporter.py
│   │   │   └── json_exporter.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── tests/
│   │
│   ├── reports/                # Reporting and analytics
│   │   ├── __init__.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── income_expense_report.py
│   │   │   ├── category_breakdown.py
│   │   │   ├── member_analysis.py
│   │   │   └── accounting_report.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── tests/
│   │
│   ├── lists/                  # Grocery lists, todo lists
│   │   ├── __init__.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── grocery_list.py
│   │   │   ├── grocery_item.py
│   │   │   ├── todo_list.py
│   │   │   └── todo_item.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── tests/
│   │
│   └── accounts/               # User authentication (future)
│       ├── __init__.py
│       ├── models.py
│       ├── views.py
│       ├── serializers.py
│       ├── urls.py
│       └── tests/
│
├── static/                     # Static files (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
│
├── media/                      # User uploads
│   ├── imports/
│   └── exports/
│
├── templates/                  # Django templates (if not using React)
│   ├── base.html
│   ├── budgets/
│   ├── imports/
│   └── reports/
│
├── frontend/                   # React frontend (if using React)
│   ├── package.json
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── utils/
│   └── public/
│
├── scripts/                    # Utility scripts
│   ├── migrate_from_smalltalk.py
│   ├── export_smalltalk_data.st  # Smalltalk script
│   └── import_legacy_data.py
│
├── docs/                       # Documentation
│   ├── api.md
│   ├── models.md
│   ├── deployment.md
│   └── migration_guide.md
│
└── deployment/                 # Deployment configs
    ├── nginx/
    │   └── nginx.conf
    ├── docker/
    │   ├── Dockerfile.backend
    │   └── Dockerfile.frontend
    └── kubernetes/  # Optional
```

---

## Development Phases & Timeline

### Phase 1: Foundation & Architecture (Weeks 1-3)

#### Week 1: Project Setup ✅ COMPLETED
- [x] Set up Git repository
- [x] Create Django project with recommended structure
- [x] Configure settings for dev/prod/test environments
- [x] Set up PostgreSQL database
- [x] Configure Docker and docker-compose
- [x] Set up virtual environment and dependencies
- [x] Configure linting (flake8, black, mypy)
- [x] Set up pytest configuration
- [x] Create .env.example file
- [x] Initialize README.md with setup instructions

#### Week 2: Database Design ✅ COMPLETED
- [x] Design database schema (ERD)
- [x] Create initial Django models (without business logic)
- [x] Set up migrations
- [x] Configure Django admin for all models
- [x] Add model managers and querysets
- [x] Create model mixins (TimestampMixin, etc.)
- [x] Write model unit tests (30 tests, 100% passing)
- [x] Set up factory_boy factories for testing

#### Week 3: Core Infrastructure + Bulk Upload (PRIORITY)
- [ ] **🎯 PRIORITY: Implement Bulk Upload UI (see priority section above)**
- [ ] **🎯 PRIORITY: Create CSV/XML parsers and import services**
- [ ] Set up Django REST Framework
- [ ] Configure CORS settings
- [ ] Set up Celery for background tasks
- [ ] Configure Redis
- [ ] Create base serializers and views
- [ ] Set up API versioning
- [ ] Configure API documentation (drf-spectacular)
- [ ] Create custom exceptions and error handlers
- [ ] Set up logging configuration

**Decision Points:**
- [x] **DECISION:** Choose frontend approach (Django Templates + Bootstrap 5 - can add HTMX later)
- [ ] **DECISION:** Determine authentication strategy (session vs JWT)
- [ ] **DECISION:** Decide on real-time updates approach (WebSockets, polling, or none)

**Note:** Built basic custom UI early (Budget list/detail views) to have something tangible to work with.

---

### 🎯 PRIORITY FEATURE: Bulk Upload for CSV/XML Data

**User Story**: As a user, I want a "Bulk Upload" button next to the "Add Transaction" button that allows me to upload CSV or XML files and automatically import and sort all the transaction data into my budget.

#### High-Priority Implementation Tasks

**Phase A: File Upload UI (Week 3 Priority)** ✅ COMPLETED
- [x] Add "Bulk Upload" button to budget detail page
- [x] Create file upload modal/page with drag-and-drop support
- [x] Add file type selector (CSV/XML)
- [x] Implement file validation (type, size limits)
- [ ] Create progress indicator during upload (optional enhancement)

**Phase B: Data Import Backend**
- [ ] Examine XML data files to understand structure and fields
- [ ] Examine CSV data files to understand structure and fields
- [ ] Document all fields found in the source data
- [ ] Map XML/CSV fields to existing Django models
- [ ] Identify any missing fields that need to be added to models

**Phase C: Update Models if Needed**
- [ ] Add any missing fields to BudgetItem model
- [ ] Add any missing fields to Budget model
- [ ] Add any missing fields to Category, Member, Source models
- [ ] Create and run migrations for new fields
- [ ] Update admin interface for new fields

**Phase D: Create Parsers and Import Services** ✅ COMPLETED
- [x] Create XML parser (apps/imports/parsers/xml_parser.py)
- [x] Create CSV parser (apps/imports/parsers/csv_parser.py)
- [x] Create unified ImportService (apps/imports/services/import_service.py)
- [x] Add data validation and error handling
- [x] Implement automatic category/member/source matching
- [x] Implement duplicate detection for imports
- [x] Add running balance recalculation after import

**Phase E: Import Preview & Validation**
- [ ] Implement preview functionality (show first 10-20 rows before import)
- [ ] Add column mapping interface for CSV files (map CSV columns to model fields)
- [ ] Show data validation warnings (missing categories, invalid amounts, etc.)
- [ ] Create confirmation step with summary (X items to import, Y duplicates found)
- [ ] Allow user to select duplicate handling strategy (skip/replace/merge)

**Phase F: Import Execution & Feedback** ✅ CORE COMPLETED
- [x] Create upload view to handle file uploads (apps/budgets/views.py bulk_upload)
- [x] Display import results (success count, errors, duplicates detected)
- [x] Handle errors gracefully with user-friendly messages
- [ ] Add real-time progress indicator during import (optional enhancement)
- [ ] Add import source indicator in transaction list (data tracked, UI pending)
- [ ] Add filters for imported vs manual transactions (future enhancement)
- [ ] Add ability to download error log if import fails (future enhancement)
- [ ] Add import history page showing past uploads (future enhancement)
- [ ] Implement import rollback/undo functionality (future enhancement)

**Phase G: Testing & Polish**
- [ ] Test CSV import with various formats
- [ ] Test XML import with real data
- [ ] Validate imported data in database
- [ ] Check running balance calculations are correct
- [ ] Verify all relationships (categories, members, sources)
- [ ] Test duplicate detection accuracy
- [ ] Test full workflow end-to-end
- [ ] Fix any data issues or mapping problems

**UI Features:**
- Upload page with drag-and-drop file support
- File format selector (CSV/XML)
- Preview table showing parsed data
- Budget selector (which budget to import into)
- Duplicate handling options (skip/replace/merge)
- Import button with confirmation dialog
- Success/error notifications

**Data Location (for script-based imports):**
- XML files: `budget-app/data/xml/` (or `apps/imports/data/xml/`)
- CSV files: `budget-app/data/csv/` (or `apps/imports/data/csv/`)

**Success Criteria:**
- All XML data successfully imported
- All CSV data successfully imported
- Data appears correctly in UI
- Running balances calculate correctly
- All categories, members, and sources properly linked
- No data loss or corruption
- **Web upload interface works smoothly for future imports**
- **Users can upload files directly through the app**

---

### Phase 2: Domain Model Migration (Weeks 4-6)

#### Week 4: Core Models Implementation

**Budget Model**
- [ ] Create Budget model with all fields
- [ ] Add model methods (calculate_balance, get_date_range, etc.)
- [ ] Create BudgetManager with custom querysets
- [ ] Add Budget serializer
- [ ] Create Budget CRUD views
- [ ] Write Budget model tests
- [ ] Configure Budget admin

**BudgetGroup Model**
- [ ] Create BudgetGroup model (hierarchical structure)
- [ ] Implement tree/hierarchy logic (MPTT or self-referential FK)
- [ ] Add BudgetGroup serializer
- [ ] Create BudgetGroup CRUD views
- [ ] Write BudgetGroup tests
- [ ] Configure BudgetGroup admin

**BudgetItem Model**
- [ ] Create BudgetItem model with all fields
- [ ] Add decimal fields for monetary values
- [ ] Implement date handling (date, posted_date, short_date)
- [ ] Add foreign keys (category, member, source, etc.)
- [ ] Create BudgetItemManager
- [ ] Add BudgetItem serializer with nested relations
- [ ] Create BudgetItem CRUD views
- [ ] Write BudgetItem model tests
- [ ] Configure BudgetItem admin with inlines

#### Week 5: Classification Models

**Category Model**
- [ ] Create Category model
- [ ] Add hierarchical category support (optional)
- [ ] Create Category serializer
- [ ] Add Category CRUD views
- [ ] Write tests
- [ ] Configure admin

**AccountingCategory Model**
- [ ] Create AccountingCategory model
- [ ] Add description field
- [ ] Create serializer and views
- [ ] Write tests
- [ ] Configure admin

**Member Model**
- [ ] Create Member model
- [ ] Add member-specific fields
- [ ] Create serializer and views
- [ ] Write tests
- [ ] Configure admin

**Source Model**
- [ ] Create Source model (income sources)
- [ ] Create serializer and views
- [ ] Write tests
- [ ] Configure admin

**CategoryVendor Model**
- [ ] Create CategoryVendor model
- [ ] Add IRS accounting text field
- [ ] Link to categories
- [ ] Create serializer and views
- [ ] Write tests
- [ ] Configure admin

#### Week 6: Advanced Models

**BudgetItemRelation Model**
- [ ] Create BudgetItemRelation model
- [ ] Implement relation types
- [ ] Add methods for linked transactions
- [ ] Create serializer and views
- [ ] Write tests
- [ ] Configure admin

**Breakout Support**
- [ ] Add breakout flag to BudgetItem
- [ ] Create breakout parent-child relationship
- [ ] Implement breakout creation logic
- [ ] Add breakout serializer fields
- [ ] Write breakout tests

**Variable Dictionary**
- [ ] Create Variable model (key-value store per budget)
- [ ] Add JSON field support
- [ ] Create serializer and views
- [ ] Write tests

**Model Enhancements**
- [ ] Add running_balance field and calculation
- [ ] Implement unique_id generation (UUID)
- [ ] Add sequence_number auto-increment
- [ ] Implement marked/flagged items
- [ ] Add pre_edit state tracking for undo
- [ ] Create model indexes for performance
- [ ] Add database constraints

---

### Phase 3: Business Logic Layer (Weeks 7-10)

#### Week 7: Budget Services

**BudgetService**
- [ ] Create BudgetService class
- [ ] Implement create_budget(name, parent_group)
- [ ] Implement update_budget(budget_id, data)
- [ ] Implement delete_budget(budget_id)
- [ ] Implement copy_budget(budget_id, new_name)
- [ ] Implement create_whatif_budget(budget_id, name)
- [ ] Add budget validation logic
- [ ] Write service tests

**TransactionService**
- [ ] Create TransactionService class
- [ ] Implement create_transaction(budget_id, data)
- [ ] Implement update_transaction(item_id, data)
- [ ] Implement delete_transaction(item_id)
- [ ] Implement bulk_create_transactions(budget_id, items)
- [ ] Implement bulk_update_transactions(items)
- [ ] Add transaction validation
- [ ] Write service tests

**BalanceCalculator**
- [ ] Create BalanceCalculator class
- [ ] Implement calculate_running_balance(budget_id)
- [ ] Implement update_balances_from_date(budget_id, date)
- [ ] Implement get_balance_at_date(budget_id, date)
- [ ] Add balance recalculation on item changes
- [ ] Optimize for performance (avoid N+1 queries)
- [ ] Write balance calculation tests

#### Week 8: Filter and Search Services

**FilterService**
- [ ] Create FilterService class
- [ ] Implement filter_by_date_range(start, end)
- [ ] Implement filter_by_categories(category_ids)
- [ ] Implement filter_by_members(member_ids)
- [ ] Implement filter_by_sources(source_ids)
- [ ] Implement filter_by_amount_range(min, max)
- [ ] Implement filter_by_accounting_categories(acc_cat_ids)
- [ ] Implement complex multi-filter logic
- [ ] Add filter serializer/schema
- [ ] Write filter tests

**SearchService**
- [ ] Create SearchService class
- [ ] Implement search_by_description(query)
- [ ] Implement search_by_reference_number(ref)
- [ ] Implement search_across_budgets(query)
- [ ] Add full-text search (PostgreSQL or elasticsearch)
- [ ] Implement search result ranking
- [ ] Write search tests

#### Week 9: Breakout and Relation Services

**BreakoutService**
- [ ] Create BreakoutService class
- [ ] Implement create_breakout(parent_item_id, breakout_items)
- [ ] Implement update_breakout(parent_item_id, breakout_items)
- [ ] Implement delete_breakout(parent_item_id)
- [ ] Add breakout validation (sum equals parent)
- [ ] Implement automatic parent value calculation
- [ ] Write breakout tests

**RelationService**
- [ ] Create RelationService class
- [ ] Implement create_relation(item1_id, item2_id, relation_type)
- [ ] Implement delete_relation(relation_id)
- [ ] Implement get_related_items(item_id)
- [ ] Add relation type definitions
- [ ] Write relation tests

#### Week 10: Reporting and Analytics

**ReportService**
- [ ] Create ReportService class
- [ ] Implement income_vs_expenses_report(budget_id, date_range)
- [ ] Implement category_breakdown_report(budget_id, date_range)
- [ ] Implement member_spending_report(budget_id, member_id, date_range)
- [ ] Implement accounting_category_report(budget_id, date_range)
- [ ] Implement monthly_trend_report(budget_id, start_month, end_month)
- [ ] Add report caching for performance
- [ ] Write report tests

**AnalyticsService**
- [ ] Create AnalyticsService class
- [ ] Implement budget_summary_stats(budget_id)
- [ ] Implement spending_trends(budget_id)
- [ ] Implement category_predictions(budget_id)
- [ ] Add data visualization helpers
- [ ] Write analytics tests

---

### Phase 4: Data Import/Export (Weeks 11-12)

#### Week 11: Import Services

**CSV Importer**
- [ ] Create CSVImporter class
- [ ] Implement parse_csv(file, column_mapping)
- [ ] Implement validate_csv_data(data)
- [ ] Implement import_csv_to_budget(budget_id, data)
- [ ] Add column mapping UI/configuration
- [ ] Implement preview before import
- [ ] Add error handling and reporting
- [ ] Write CSV import tests

**OFX/QFX Importer**
- [ ] Create OFXImporter class using ofxparse
- [ ] Implement parse_ofx_file(file)
- [ ] Implement map_ofx_to_budget_items(ofx_data)
- [ ] Add account matching logic
- [ ] Implement category auto-mapping (rules-based)
- [ ] Write OFX import tests

**Quicken Importer**
- [ ] Create QuickenImporter class
- [ ] Implement parse_quicken_file(file)
- [ ] Map Quicken fields to BudgetItem fields
- [ ] Handle Quicken categories
- [ ] Write Quicken import tests

**Duplicate Detection**
- [ ] Create DuplicateDetector class
- [ ] Implement find_duplicates(budget_id, new_items)
- [ ] Add matching criteria (date, amount, description)
- [ ] Implement fuzzy matching for descriptions
- [ ] Add user confirmation flow for duplicates
- [ ] Write duplicate detection tests

**Import Tracking**
- [ ] Create ImportTracker model
- [ ] Track import source, date, file name
- [ ] Link imported items to import record
- [ ] Implement import history view
- [ ] Add rollback/undo import functionality
- [ ] Write import tracking tests

#### Week 12: Export Services

**CSV Exporter**
- [ ] Create CSVExporter class
- [ ] Implement export_budget_to_csv(budget_id, filters)
- [ ] Add column selection/configuration
- [ ] Implement export with running balances
- [ ] Write CSV export tests

**Excel Exporter**
- [ ] Create ExcelExporter class using openpyxl
- [ ] Implement export_budget_to_excel(budget_id, filters)
- [ ] Add multiple sheets (items, summary, charts)
- [ ] Format cells (currency, dates)
- [ ] Add Excel formulas for totals
- [ ] Write Excel export tests

**PDF Exporter**
- [ ] Create PDFExporter class using reportlab
- [ ] Implement export_budget_to_pdf(budget_id, filters)
- [ ] Design PDF report layout
- [ ] Add charts and summaries
- [ ] Implement page breaks and headers
- [ ] Write PDF export tests

**JSON Exporter**
- [ ] Create JSONExporter class
- [ ] Implement export_budget_to_json(budget_id)
- [ ] Include all related data (categories, members, etc.)
- [ ] Implement import_from_json(file)
- [ ] Use for backup/restore functionality
- [ ] Write JSON export/import tests

---

### Phase 5: User Interface (Weeks 13-18)

#### Frontend Decision Implementation

**Option A: React SPA** (if chosen)

**Week 13-14: React Setup and Core Components**
- [ ] Initialize React app with Create React App or Vite
- [ ] Set up React Router
- [ ] Configure Axios for API calls
- [ ] Set up state management (Redux/Context API)
- [ ] Choose UI framework (Material-UI, Ant Design, etc.)
- [ ] Create base layout components
- [ ] Set up authentication flow
- [ ] Create error boundary components
- [ ] Configure environment variables

**Week 15-16: Budget Management UI**
- [ ] Create BudgetTree component (hierarchical view)
- [ ] Create BudgetList component
- [ ] Create BudgetDetail component
- [ ] Create BudgetForm component (create/edit)
- [ ] Implement budget group navigation
- [ ] Add budget actions (copy, delete, whatif)
- [ ] Create budget notes editor
- [ ] Add responsive design

**Week 17-18: Transaction Management UI**
- [ ] Create TransactionList component with filtering
- [ ] Create TransactionForm component (add/edit)
- [ ] Implement inline editing
- [ ] Create filter panel component
- [ ] Add date range picker
- [ ] Create category/member/source selectors
- [ ] Implement multi-select operations
- [ ] Add running balance display
- [ ] Create breakout editor component
- [ ] Add transaction search

**Option B: Django Templates + HTMX** (if chosen)

**Week 13-14: Template Setup**
- [ ] Set up base templates with Bootstrap 5
- [ ] Configure HTMX
- [ ] Create navigation and layout templates
- [ ] Set up Django forms for all models
- [ ] Configure crispy-forms
- [ ] Create reusable template tags
- [ ] Set up JavaScript for interactions

**Week 15-16: Budget Management Templates**
- [ ] Create budget tree view template
- [ ] Create budget list template
- [ ] Create budget detail template
- [ ] Create budget form templates
- [ ] Implement HTMX for dynamic updates
- [ ] Add budget group navigation
- [ ] Create budget notes editor

**Week 17-18: Transaction Management Templates**
- [ ] Create transaction list template
- [ ] Create transaction form templates
- [ ] Implement filter panel
- [ ] Add HTMX for inline editing
- [ ] Create pagination
- [ ] Add multi-select functionality
- [ ] Create breakout editor templates
- [ ] Add search functionality

#### Shared UI Work (Both Options)

**Import/Export UI**
- [ ] Create import wizard component/template
- [ ] Add file upload functionality
- [ ] Create column mapping interface
- [ ] Add import preview
- [ ] Create duplicate resolution UI
- [ ] Add export options form
- [ ] Create export download functionality

**Reports and Analytics UI**
- [ ] Create reports dashboard
- [ ] Add chart components (Chart.js)
- [ ] Create income vs expenses chart
- [ ] Create category breakdown pie chart
- [ ] Create monthly trend line chart
- [ ] Add date range selection for reports
- [ ] Create printable report views
- [ ] Add report export options

**Lists UI (Grocery, Todo)**
- [ ] Create grocery list components/templates
- [ ] Create todo list components/templates
- [ ] Add drag-and-drop for ordering
- [ ] Implement list item editing
- [ ] Add completion tracking

---

### Phase 6: Advanced Features (Weeks 19-22)

#### Week 19: Notes System
- [ ] Implement budget notes (rich text editor)
- [ ] Implement group notes
- [ ] Implement application-level notes
- [ ] Add notes change tracking
- [ ] Create notes history view
- [ ] Add autosave functionality
- [ ] Write notes tests

#### Week 20: Scenarios and Copying
- [ ] Enhance copy_budget to deep copy all relations
- [ ] Implement whatif budget scenario creation
- [ ] Add scenario comparison view
- [ ] Implement scenario merging
- [ ] Add scenario labels/tags
- [ ] Write scenario tests

#### Week 21: Multi-Selection Operations
- [ ] Implement bulk edit transactions
- [ ] Add bulk delete with confirmation
- [ ] Implement bulk categorization
- [ ] Add bulk export selected items
- [ ] Implement bulk tag/mark items
- [ ] Write bulk operation tests

#### Week 22: Backup and Archive
- [ ] Create backup service
- [ ] Implement automatic backups (Celery task)
- [ ] Add manual backup trigger
- [ ] Create archive functionality
- [ ] Implement restore from backup
- [ ] Add backup management UI
- [ ] Write backup/restore tests

---

### Phase 7: Testing & Quality Assurance (Weeks 23-24)

#### Week 23: Comprehensive Testing
- [ ] Achieve 80%+ code coverage
- [ ] Write integration tests for all API endpoints
- [ ] Create end-to-end tests (Selenium/Playwright)
- [ ] Test all import/export scenarios
- [ ] Test edge cases and error handling
- [ ] Performance testing (load tests with locust)
- [ ] Test database constraints and validation
- [ ] Test concurrent user scenarios

#### Week 24: Quality Assurance
- [ ] Code review of all modules
- [ ] Security audit (SQL injection, XSS, CSRF)
- [ ] Accessibility audit (WCAG 2.1)
- [ ] Browser compatibility testing
- [ ] Mobile responsiveness testing
- [ ] Documentation review
- [ ] User acceptance testing prep
- [ ] Bug fixing and refinement

---

### Phase 8: Data Migration from Smalltalk (Weeks 25-26)

#### Week 25: Smalltalk Data Export
- [ ] **Write Smalltalk export script** (run in VisualWorks)
- [ ] Export Budget objects to JSON/CSV
- [ ] Export BudgetItems to CSV
- [ ] Export all lookup tables (categories, members, sources)
- [ ] Export budget groups hierarchy
- [ ] Export relations and breakouts
- [ ] Export notes and metadata
- [ ] Validate exported data integrity

#### Week 26: Python Data Import
- [ ] Create migration script (Django management command)
- [ ] Import budget groups (hierarchy first)
- [ ] Import categories, members, sources
- [ ] Import budgets with all metadata
- [ ] Import budget items with relationships
- [ ] Import accounting categories and mappings
- [ ] Import relations and breakouts
- [ ] Validate imported data
- [ ] Test application with real data
- [ ] Fix data migration issues
- [ ] Create migration documentation

**Migration Checklist:**
- [ ] Backup Smalltalk image before export
- [ ] Verify all budget groups imported correctly
- [ ] Verify hierarchy structure preserved
- [ ] Verify all transactions imported
- [ ] Verify running balances match
- [ ] Verify categories and mappings correct
- [ ] Verify member and source data
- [ ] Verify notes preserved
- [ ] Verify import source tracking
- [ ] Compare report totals Smalltalk vs Django

---

### Phase 9: Deployment (Week 27-28)

#### Week 27: Deployment Preparation
- [ ] Create production settings
- [ ] Configure environment variables
- [ ] Set up static file serving (Whitenoise or S3)
- [ ] Configure media file storage
- [ ] Set up production database (PostgreSQL)
- [ ] Configure Redis for production
- [ ] Set up Celery workers
- [ ] Configure logging and monitoring
- [ ] Set up error tracking (Sentry)
- [ ] Create deployment scripts

#### Week 28: Deployment and Launch
- [ ] Build Docker images
- [ ] Set up Docker Compose for production
- [ ] Configure nginx reverse proxy
- [ ] Set up SSL certificates (Let's Encrypt)
- [ ] Deploy to production server
- [ ] Run database migrations
- [ ] Import production data
- [ ] Configure automated backups
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Performance tuning
- [ ] Create runbooks for common issues
- [ ] User training and documentation
- [ ] Go-live!

---

## Detailed Design Decisions

### 1. Database Schema Design

#### Budget Model
```python
class Budget(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    changes_made = models.BooleanField(default=False)
    file_name_string = models.CharField(max_length=500, blank=True)
    list_number = models.IntegerField(null=True, blank=True)
    current_sequence_number = models.IntegerField(default=0)
    is_copy = models.BooleanField(default=False)
    is_whatif = models.BooleanField(default=False)

    # Relations
    group = models.ForeignKey('BudgetGroup', on_delete=models.CASCADE, related_name='budgets')
    categories = models.ManyToManyField('Category')
    accounting_categories = models.ManyToManyField('AccountingCategory')
    members = models.ManyToManyField('Member')
    sources = models.ManyToManyField('Source')

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['group', 'name']),
        ]
```

#### BudgetItem Model
```python
class BudgetItem(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    unique_id = models.CharField(max_length=100, unique=True)
    sequence_number = models.IntegerField()

    # Core fields
    budget = models.ForeignKey('Budget', on_delete=models.CASCADE, related_name='items')
    category = models.ForeignKey('Category', on_delete=PROTECT)
    monitary_value = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.CharField(max_length=500)

    # Dates
    date = models.DateField()
    posted_date = models.DateField(null=True, blank=True)
    short_date = models.CharField(max_length=50, blank=True)

    # Relations
    member = models.ForeignKey('Member', on_delete=PROTECT, null=True)
    source = models.ForeignKey('Source', on_delete=PROTECT, null=True)
    category_vendor = models.ForeignKey('CategoryVendor', on_delete=SET_NULL, null=True)
    accounting_categories = models.ManyToManyField('AccountingCategory')

    # Tracking
    running_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    import_source = models.CharField(max_length=255, blank=True)
    reference_number = models.CharField(max_length=100, blank=True)
    update_timestamp = models.DateTimeField(auto_now=True)

    # State
    imported = models.BooleanField(default=False)
    marked = models.BooleanField(default=False)
    is_breakout = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=CASCADE, null=True, related_name='breakouts')

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['date', 'sequence_number']
        indexes = [
            models.Index(fields=['budget', 'date']),
            models.Index(fields=['category']),
            models.Index(fields=['member']),
            models.Index(fields=['source']),
            models.Index(fields=['unique_id']),
        ]
```

#### BudgetGroup Model (Hierarchical)
```python
class BudgetGroup(TimeStampedModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=CASCADE, null=True, related_name='children')
    file_name_string = models.CharField(max_length=500)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']
```

#### Category Model
```python
class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    # Optional: hierarchical categories
    parent = models.ForeignKey('self', on_delete=SET_NULL, null=True, related_name='subcategories')

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']
```

#### AccountingCategory Model
```python
class AccountingCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Accounting Categories'
        ordering = ['name']
```

#### Member Model
```python
class Member(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ['name']
```

#### Source Model
```python
class Source(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255, unique=True)
    source_type = models.CharField(max_length=50, choices=[
        ('income', 'Income'),
        ('transfer', 'Transfer'),
        ('other', 'Other'),
    ])

    class Meta:
        ordering = ['name']
```

#### CategoryVendor Model
```python
class CategoryVendor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=255, unique=True)
    category = models.ForeignKey('Category', on_delete=CASCADE)
    irs_accounting_text = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
```

#### BudgetItemRelation Model
```python
class BudgetItemRelation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    item1 = models.ForeignKey('BudgetItem', on_delete=CASCADE, related_name='relations_from')
    item2 = models.ForeignKey('BudgetItem', on_delete=CASCADE, related_name='relations_to')
    relation_type = models.CharField(max_length=50, choices=[
        ('linked', 'Linked'),
        ('transfer', 'Transfer'),
        ('split_from', 'Split From'),
        ('correction', 'Correction'),
    ])

    class Meta:
        unique_together = [['item1', 'item2', 'relation_type']]
```

#### ImportTracker Model
```python
class ImportTracker(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    budget = models.ForeignKey('Budget', on_delete=CASCADE)
    import_date = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=500)
    file_type = models.CharField(max_length=50)  # csv, ofx, quicken
    items_imported = models.IntegerField()
    duplicates_found = models.IntegerField()
    source_name = models.CharField(max_length=255)

    class Meta:
        ordering = ['-import_date']
```

### 2. API Design

#### REST API Structure
```
/api/v1/
├── budgets/
│   ├── GET    /                      # List all budgets
│   ├── POST   /                      # Create budget
│   ├── GET    /{id}/                 # Get budget detail
│   ├── PUT    /{id}/                 # Update budget
│   ├── PATCH  /{id}/                 # Partial update
│   ├── DELETE /{id}/                 # Delete budget
│   ├── POST   /{id}/copy/            # Copy budget
│   ├── POST   /{id}/whatif/          # Create whatif scenario
│   ├── GET    /{id}/items/           # List budget items
│   ├── POST   /{id}/items/           # Create budget item
│   ├── GET    /{id}/summary/         # Budget summary stats
│   └── GET    /{id}/balance/         # Balance over time
│
├── budget-groups/
│   ├── GET    /                      # List all groups
│   ├── POST   /                      # Create group
│   ├── GET    /{id}/                 # Get group detail
│   ├── PUT    /{id}/                 # Update group
│   ├── DELETE /{id}/                 # Delete group
│   └── GET    /{id}/tree/            # Get group hierarchy
│
├── budget-items/
│   ├── GET    /                      # List items (filterable)
│   ├── POST   /                      # Create item
│   ├── GET    /{id}/                 # Get item detail
│   ├── PUT    /{id}/                 # Update item
│   ├── DELETE /{id}/                 # Delete item
│   ├── POST   /bulk/                 # Bulk create
│   ├── PUT    /bulk/                 # Bulk update
│   ├── DELETE /bulk/                 # Bulk delete
│   ├── POST   /{id}/breakout/        # Create breakout
│   └── GET    /{id}/related/         # Get related items
│
├── categories/
│   ├── GET    /                      # List all
│   ├── POST   /                      # Create
│   ├── GET    /{id}/                 # Detail
│   ├── PUT    /{id}/                 # Update
│   └── DELETE /{id}/                 # Delete
│
├── accounting-categories/            # Same CRUD as categories
├── members/                          # Same CRUD as categories
├── sources/                          # Same CRUD as categories
├── vendors/                          # Same CRUD as categories
│
├── imports/
│   ├── POST   /csv/                  # Upload CSV
│   ├── POST   /ofx/                  # Upload OFX
│   ├── POST   /quicken/              # Upload Quicken
│   ├── GET    /{id}/preview/         # Preview import
│   ├── POST   /{id}/confirm/         # Confirm import
│   └── GET    /history/              # Import history
│
├── exports/
│   ├── POST   /csv/                  # Export to CSV
│   ├── POST   /excel/                # Export to Excel
│   ├── POST   /pdf/                  # Export to PDF
│   └── POST   /json/                 # Export to JSON
│
├── reports/
│   ├── GET    /income-expense/       # Income vs expense
│   ├── GET    /category-breakdown/   # Category breakdown
│   ├── GET    /member-spending/      # Member spending
│   └── GET    /accounting/           # Accounting report
│
├── grocery-lists/                    # Grocery list CRUD
├── todo-lists/                       # Todo list CRUD
│
└── search/
    └── GET    /?q=query              # Global search
```

#### Example API Request/Response

**GET /api/v1/budgets/{id}/items/?category=xxx&date_from=2024-01-01&date_to=2024-12-31**

Response:
```json
{
  "count": 150,
  "next": "http://api/v1/budgets/{id}/items/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid-here",
      "unique_id": "ITEM-2024-001",
      "sequence_number": 1,
      "category": {
        "id": "cat-uuid",
        "name": "Groceries"
      },
      "monitary_value": "-125.50",
      "description": "Weekly grocery shopping",
      "date": "2024-01-15",
      "posted_date": "2024-01-16",
      "member": {
        "id": "member-uuid",
        "name": "John"
      },
      "source": null,
      "running_balance": "2500.75",
      "import_source": "Chase_Statement_2024-01.csv",
      "imported": true,
      "marked": false,
      "is_breakout": false,
      "accounting_categories": [
        {
          "id": "acc-uuid",
          "name": "Personal Expenses"
        }
      ]
    }
  ]
}
```

### 3. Frontend Architecture (if React)

#### Component Hierarchy
```
App
├── Layout
│   ├── Header
│   ├── Sidebar
│   └── Footer
├── Routes
│   ├── Dashboard
│   ├── BudgetManager
│   │   ├── BudgetTree
│   │   ├── BudgetList
│   │   └── BudgetDetail
│   │       ├── TransactionList
│   │       │   ├── FilterPanel
│   │       │   ├── TransactionTable
│   │       │   └── Pagination
│   │       ├── TransactionForm
│   │       └── BudgetSummary
│   ├── Reports
│   │   ├── IncomeExpenseChart
│   │   ├── CategoryBreakdown
│   │   └── TrendAnalysis
│   ├── Import
│   │   ├── FileUpload
│   │   ├── ColumnMapping
│   │   ├── Preview
│   │   └── DuplicateResolution
│   └── Settings
│       ├── Categories
│       ├── Members
│       ├── Sources
│       └── AccountingCategories
```

#### State Management (Redux example)
```javascript
store/
├── budgets/
│   ├── budgetsSlice.js
│   ├── budgetItemsSlice.js
│   └── budgetSelectors.js
├── categories/
│   └── categoriesSlice.js
├── filters/
│   └── filtersSlice.js
├── ui/
│   └── uiSlice.js
└── store.js
```

### 4. Security Considerations

- [ ] **Authentication:** Implement JWT or session-based auth
- [ ] **Authorization:** Add user permissions (view, edit, delete)
- [ ] **CSRF Protection:** Enable Django CSRF middleware
- [ ] **XSS Protection:** Sanitize user inputs
- [ ] **SQL Injection:** Use Django ORM (parameterized queries)
- [ ] **File Upload Security:** Validate file types, scan for malware
- [ ] **Rate Limiting:** Add rate limiting to API endpoints
- [ ] **HTTPS:** Enforce HTTPS in production
- [ ] **Secrets Management:** Use environment variables, never commit secrets
- [ ] **Database Security:** Use strong passwords, restrict access
- [ ] **Audit Logging:** Log all data modifications
- [ ] **Backup Encryption:** Encrypt sensitive backups

### 5. Performance Optimization

- [ ] **Database Indexing:** Add indexes on frequently queried fields
- [ ] **Query Optimization:** Use select_related/prefetch_related
- [ ] **Caching:** Use Redis for frequently accessed data
- [ ] **Pagination:** Implement pagination for large datasets
- [ ] **Lazy Loading:** Load data on demand in frontend
- [ ] **Database Connection Pooling:** Configure pgBouncer
- [ ] **Static File CDN:** Serve static files from CDN
- [ ] **Compression:** Enable gzip compression
- [ ] **Async Tasks:** Use Celery for background processing
- [ ] **Database Read Replicas:** For scaling reads

### 6. Error Handling Strategy

```python
# Custom exceptions
class BudgetException(Exception):
    """Base exception for budget app"""
    pass

class BudgetNotFoundError(BudgetException):
    pass

class InvalidTransactionError(BudgetException):
    pass

class ImportError(BudgetException):
    pass

class DuplicateDetectedError(BudgetException):
    pass

# Global exception handler
@api_view(['GET'])
def handle_exception(exc, context):
    if isinstance(exc, BudgetException):
        return Response({
            'error': str(exc),
            'type': exc.__class__.__name__
        }, status=status.HTTP_400_BAD_REQUEST)

    # Log unexpected errors
    logger.exception("Unexpected error occurred")
    return Response({
        'error': 'An unexpected error occurred'
    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
```

---

## Key Files from Smalltalk

### Source Code Files (.st)
- `Budget Base.st` - Core Budget class and related classes
- `Budget UIs.st` - UI components (ApplicationModel classes)
- `BudgetList.st` - Budget list handling
- `BudgetItem.st` - Transaction/item class
- `CostAccounting4.st` - Cost accounting functionality
- `UI_BudgetApplicationModel.st` - Main application model
- `CategoryVendor.st` - Vendor/category mappings

### Data Files
- Budget groups stored in: `E:\Geek Squad Data Backup 2025-01-14\from 2TB WD Green\Hdrive\Cincom_old\Groups_bs`
- CSV exports in various `*.csv` files
- Notes in `application.notes`

---

## Migration from Smalltalk - Detailed Plan

### Step 1: Analyze Smalltalk Code
- [ ] Read all .st fileouts
- [ ] Document class hierarchy
- [ ] Document instance variables for each class
- [ ] Document key methods and business logic
- [ ] Identify all UI components
- [ ] Map Smalltalk patterns to Python equivalents

### Step 2: Export Data from Smalltalk
Create a Smalltalk script to export data:

```smalltalk
"Run this in VisualWorks workspace"

| budgetGroups allBudgets exportDir |

exportDir := 'E:\exports\' asFilename.
exportDir exists ifFalse: [exportDir makeDirectory].

"Export budget groups"
UI_BudgetTool readGroups.
budgetGroups := UI_BudgetTool new groups.
BudgetExporter exportGroups: budgetGroups to: exportDir , 'groups.json'.

"Export all budgets with items"
allBudgets := OrderedCollection new.
budgetGroups do: [:group |
    group budgets do: [:budget |
        allBudgets add: budget.
    ]
].
BudgetExporter exportBudgets: allBudgets to: exportDir , 'budgets.json'.

"Export lookup tables"
BudgetExporter exportCategories to: exportDir , 'categories.json'.
BudgetExporter exportAccountingCategories to: exportDir , 'accounting_categories.json'.
BudgetExporter exportMembers to: exportDir , 'members.json'.
BudgetExporter exportSources to: exportDir , 'sources.json'.
BudgetExporter exportVendors to: exportDir , 'vendors.json'.

Transcript show: 'Export complete!'.
```

### Step 3: Import to Django
Create Django management command:

```python
# python manage.py import_from_smalltalk

from django.core.management.base import BaseCommand
import json
from apps.budgets.models import Budget, BudgetItem, Category, ...

class Command(BaseCommand):
    help = 'Import data from Smalltalk export files'

    def handle(self, *args, **options):
        # Import categories first (no dependencies)
        self.import_categories()
        self.import_members()
        self.import_sources()

        # Import budget groups
        self.import_budget_groups()

        # Import budgets
        self.import_budgets()

        # Import budget items
        self.import_budget_items()

        # Import relations
        self.import_relations()

        self.stdout.write(self.style.SUCCESS('Import complete!'))
```

---

## Environment Setup

### .env.example
```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=budget_app
DB_USER=budget_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Frontend
FRONTEND_URL=http://localhost:3000

# File uploads
MEDIA_ROOT=/path/to/media
MAX_UPLOAD_SIZE=10485760  # 10MB

# Email (for notifications)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password

# Logging
LOG_LEVEL=INFO
```

---

## Testing Strategy

### Unit Tests
- Test all models (validation, methods, managers)
- Test all services (business logic)
- Test all serializers
- Test utilities and helpers

### Integration Tests
- Test API endpoints end-to-end
- Test import/export workflows
- Test complex business logic scenarios
- Test filter combinations

### End-to-End Tests
- Test user workflows (create budget, add transactions, etc.)
- Test import wizard flow
- Test report generation
- Test multi-user scenarios (if applicable)

### Performance Tests
- Load test API endpoints
- Test with large datasets (10k+ transactions)
- Test concurrent operations
- Test query performance

---

## Documentation Requirements

### Code Documentation
- [ ] Docstrings for all classes and methods
- [ ] Inline comments for complex logic
- [ ] Type hints throughout codebase

### API Documentation
- [ ] OpenAPI/Swagger documentation
- [ ] Example requests/responses
- [ ] Authentication guide
- [ ] Error code reference

### User Documentation
- [ ] User guide with screenshots
- [ ] Import/export guide
- [ ] Report generation guide
- [ ] FAQ section

### Developer Documentation
- [ ] Setup guide
- [ ] Architecture overview
- [ ] Database schema documentation
- [ ] Deployment guide
- [ ] Contributing guide

---

## Success Criteria

### Functional Requirements
- [ ] All budget operations work (CRUD)
- [ ] Transaction filtering works correctly
- [ ] Import from CSV/OFX/Quicken works
- [ ] Export to CSV/Excel/PDF works
- [ ] Running balance calculations are accurate
- [ ] All reports generate correctly
- [ ] Breakouts function properly
- [ ] Transaction relations work

### Non-Functional Requirements
- [ ] Page load time < 2 seconds
- [ ] API response time < 500ms
- [ ] Support 100+ concurrent users
- [ ] 99.9% uptime
- [ ] Mobile responsive design
- [ ] WCAG 2.1 AA compliance
- [ ] 80%+ test coverage

### Data Migration Success
- [ ] All budgets migrated
- [ ] All transactions migrated
- [ ] All categories/members/sources migrated
- [ ] Hierarchy structure preserved
- [ ] Running balances match
- [ ] No data loss

---

## Risks and Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Data loss during migration | High | Medium | Multiple backups, staged migration, validation scripts |
| Performance issues with large datasets | High | Medium | Indexing, caching, pagination, query optimization |
| Scope creep | Medium | High | Strict MVP definition, phased approach |
| Complex business logic not understood | High | Medium | Thorough Smalltalk code analysis, incremental testing |
| Frontend complexity | Medium | Medium | Choose simpler Django templates if React too complex |
| Timeline slippage | Medium | High | Buffer time, prioritize MVP features |

---

## Post-Launch Roadmap

### Version 1.1 (Enhancements)
- [ ] Multi-user support with permissions
- [ ] Budget sharing/collaboration
- [ ] Mobile apps (React Native)
- [ ] Advanced analytics and forecasting
- [ ] Budget templates
- [ ] Recurring transaction support
- [ ] Email notifications
- [ ] Two-factor authentication

### Version 2.0 (Advanced Features)
- [ ] Machine learning for category prediction
- [ ] Automatic bank synchronization
- [ ] Investment tracking
- [ ] Debt management
- [ ] Goal tracking
- [ ] Multi-currency support
- [ ] API for third-party integrations

---

## Resources and References

### Django Resources
- Django documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Django best practices: https://github.com/HackSoftware/Django-Styleguide

### Libraries
- ofxparse: https://github.com/jseutter/ofxparse
- openpyxl: https://openpyxl.readthedocs.io/
- reportlab: https://www.reportlab.com/docs/reportlab-userguide.pdf
- Celery: https://docs.celeryq.dev/

### Smalltalk Resources
- VisualWorks documentation (for understanding source)
- BOSS (Binary Object Storage) format documentation

---

## Notes

- The Smalltalk application uses BOSS format for some data persistence
- Budget groups are stored in filesystem hierarchy
- The application has extensive filtering capabilities - need to replicate
- Running balance is critical - must be calculated correctly
- Import duplicate detection is sophisticated - study the logic
- The UI has many keyboard shortcuts - consider for new UI
- Application supports "Copy" and "WhatIf" budget scenarios
- Notes system has change tracking
- Breakouts must sum to parent transaction amount

---

## Contact and Support

For questions during development:
- Review Smalltalk source code in `.st` files
- Check existing data structure in PostgreSQL (if accessible)
- Refer to this roadmap document

---

**Last Updated:** 2025-01-14
**Version:** 1.0
**Status:** Planning Phase
