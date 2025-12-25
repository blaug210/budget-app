"""
Django management command to import budget items from Smalltalk CSV export.

The CSV file uses '^' as delimiter with the following columns:
Name^Month^Date^Groups^Category^Accounting Categories^ID^Source^Description^Amount

Usage:
    python manage.py import_budget_items /path/to/budgetItems.02.csv
"""

import csv
from decimal import Decimal, InvalidOperation
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.budgets.models import (
    Category, Member, Source, BudgetGroup, Budget, BudgetItem
)


class Command(BaseCommand):
    help = 'Import budget items from Smalltalk CSV export (^ delimited)'

    def add_arguments(self, parser):
        parser.add_argument(
            'csv_file',
            type=str,
            help='Path to budgetItems.02.csv file'
        )
        parser.add_argument(
            '--budget-name',
            type=str,
            default='Historical Data 2001-2025',
            help='Name of budget to import into (will be created if not exists)',
        )
        parser.add_argument(
            '--group-name',
            type=str,
            default='Historical',
            help='Name of budget group (will be created if not exists)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Parse the file but do not import (shows statistics)',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Number of items to import per batch (default: 1000)',
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        budget_name = options['budget_name']
        group_name = options['group_name']
        dry_run = options.get('dry_run', False)
        batch_size = options.get('batch_size', 1000)

        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('BUDGET ITEMS IMPORT'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(f'File: {csv_file}')
        self.stdout.write(f'Budget: {budget_name}')
        self.stdout.write(f'Group: {group_name}')
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No data will be imported'))
        self.stdout.write('')

        # Cache for related objects
        self.categories = {}
        self.members = {}
        self.sources = {}

        try:
            # Create or get budget group and budget
            if not dry_run:
                budget_group, created = BudgetGroup.objects.get_or_create(
                    name=group_name,
                    defaults={'notes': 'Historical data from Smalltalk'}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'✓ Created budget group: {group_name}'))

                budget, created = Budget.objects.get_or_create(
                    name=budget_name,
                    defaults={
                        'group': budget_group,
                        'notes': 'Imported from Smalltalk budgetItems.02.csv'
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'✓ Created budget: {budget_name}'))
                else:
                    self.stdout.write(self.style.WARNING(f'⚠️  Using existing budget: {budget_name}'))
                self.stdout.write('')
            else:
                budget = None

            # Parse and import
            stats = self.parse_and_import(csv_file, budget, dry_run, batch_size)

            # Print statistics
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('='*70))
            self.stdout.write(self.style.SUCCESS('IMPORT STATISTICS'))
            self.stdout.write(self.style.SUCCESS('='*70))
            self.stdout.write(f'Total lines processed: {stats["total_lines"]:,}')
            self.stdout.write(f'Transactions imported: {stats["imported"]:,}')
            self.stdout.write(f'Skipped (errors): {stats["errors"]:,}')
            self.stdout.write(f'Date range: {stats["min_date"]} to {stats["max_date"]}')
            self.stdout.write(f'Unique members: {len(self.members)}')
            self.stdout.write(f'Unique categories: {len(self.categories)}')
            self.stdout.write(f'Unique sources: {len(self.sources)}')
            self.stdout.write('')

            if not dry_run:
                self.stdout.write(self.style.SUCCESS('✓ IMPORT COMPLETED SUCCESSFULLY!'))
            else:
                self.stdout.write(self.style.WARNING('DRY RUN COMPLETE - Run without --dry-run to import'))
            self.stdout.write(self.style.SUCCESS('='*70))

        except Exception as e:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('='*70))
            self.stdout.write(self.style.ERROR(f'✗ IMPORT FAILED: {str(e)}'))
            self.stdout.write(self.style.ERROR('='*70))
            import traceback
            self.stdout.write(traceback.format_exc())
            raise CommandError(f'Import failed: {e}')

    def parse_and_import(self, csv_file, budget, dry_run, batch_size):
        """Parse CSV file and import items."""
        stats = {
            'total_lines': 0,
            'imported': 0,
            'errors': 0,
            'min_date': None,
            'max_date': None,
        }

        batch = []

        with open(csv_file, 'r', encoding='utf-8', errors='replace') as f:
            # Skip first 2 header lines
            next(f)  # File path line
            next(f)  # Date range line

            # Read CSV with ^ delimiter
            reader = csv.DictReader(f, delimiter='^')

            for row in reader:
                stats['total_lines'] += 1

                try:
                    # Parse date (format: YYYYMMDD HH:MM:SS)
                    date_str = row.get('Date', '').strip()
                    if date_str:
                        date = datetime.strptime(date_str[:8], '%Y%m%d').date()

                        # Update date range
                        if stats['min_date'] is None or date < stats['min_date']:
                            stats['min_date'] = date
                        if stats['max_date'] is None or date > stats['max_date']:
                            stats['max_date'] = date
                    else:
                        date = None

                    # Parse amount
                    amount_str = row.get('Amount', '0').strip()
                    try:
                        amount = Decimal(amount_str)
                    except (InvalidOperation, ValueError):
                        amount = Decimal('0')

                    # Extract fields
                    member_name = row.get('Name', '').strip()
                    category_name = row.get('Category', '').strip()
                    source_name = row.get('Source', '').strip()
                    description = row.get('Description', '').strip()
                    reference_id = row.get('ID', '').strip()

                    if not dry_run:
                        # Get or create related objects
                        member = self.get_or_create_member(member_name) if member_name else None
                        category = self.get_or_create_category(category_name) if category_name else None
                        source = self.get_or_create_source(source_name) if source_name else None

                        # Create budget item
                        item = BudgetItem(
                            budget=budget,
                            date=date,
                            description=description,
                            monitary_value=amount,
                            reference_number=reference_id,
                            sequence_number=stats['imported'] + 1
                        )

                        batch.append((item, member, category, source))

                        # Bulk create when batch is full
                        if len(batch) >= batch_size:
                            self.save_batch(batch)
                            stats['imported'] += len(batch)
                            batch = []
                            self.stdout.write(f'  → {stats["imported"]:,} transactions imported...', ending='\r')
                    else:
                        # Just count in dry run mode
                        if member_name:
                            self.members[member_name] = True
                        if category_name:
                            self.categories[category_name] = True
                        if source_name:
                            self.sources[source_name] = True
                        stats['imported'] += 1

                except Exception as e:
                    stats['errors'] += 1
                    if stats['errors'] <= 10:  # Show first 10 errors
                        self.stdout.write(self.style.WARNING(
                            f'  ⚠️  Error on line {stats["total_lines"]}: {str(e)}'
                        ))

            # Save remaining batch
            if batch and not dry_run:
                self.save_batch(batch)
                stats['imported'] += len(batch)
                self.stdout.write('')

        return stats

    def get_or_create_member(self, name):
        """Get or create a Member object."""
        if name not in self.members:
            member, created = Member.objects.get_or_create(
                name=name
            )
            self.members[name] = member
        return self.members[name]

    def get_or_create_category(self, name):
        """Get or create a Category object."""
        if name not in self.categories:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'description': f'Auto-imported: {name}'}
            )
            self.categories[name] = category
        return self.categories[name]

    def get_or_create_source(self, name):
        """Get or create a Source object."""
        if name not in self.sources:
            source, created = Source.objects.get_or_create(
                name=name,
                defaults={
                    'source_type': 'other'
                }
            )
            self.sources[name] = source
        return self.sources[name]

    def save_batch(self, batch):
        """Save a batch of budget items with their relationships."""
        items = [item for item, _, _, _ in batch]

        # Bulk create items
        created_items = BudgetItem.objects.bulk_create(items)

        # Set M2M relationships
        for idx, (item, member, category, source) in enumerate(batch):
            created_item = created_items[idx]
            if member:
                created_item.members.add(member)
            if category:
                created_item.categories.add(category)
            if source:
                created_item.sources.add(source)
