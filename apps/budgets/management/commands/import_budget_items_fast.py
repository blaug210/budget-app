"""
Fast import for budget items from Smalltalk CSV export.
Optimized version with member/category/source support.

Usage:
    python manage.py import_budget_items_fast /path/to/budgetItems.02.csv
"""

import csv
from decimal import Decimal, InvalidOperation
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.budgets.models import BudgetGroup, Budget, BudgetItem, Member, Category, Source


class Command(BaseCommand):
    help = 'Fast import of budget items (no categories/members/sources)'

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
            help='Name of budget to import into',
        )
        parser.add_argument(
            '--group-name',
            type=str,
            default='Historical',
            help='Name of budget group',
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=5000,
            help='Batch size (default: 5000)',
        )

    def handle(self, *args, **options):
        csv_file = options['csv_file']
        budget_name = options['budget_name']
        group_name = options['group_name']
        batch_size = options.get('batch_size', 5000)

        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('FAST BUDGET ITEMS IMPORT'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(f'File: {csv_file}')
        self.stdout.write(f'Budget: {budget_name}')
        self.stdout.write(f'Batch size: {batch_size}')
        self.stdout.write('')

        # Caches for members, categories, sources
        self.members_cache = {}
        self.categories_cache = {}
        self.sources_cache = {}

        try:
            # Create or get budget group and budget
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

            # Parse and import
            stats = self.parse_and_import(csv_file, budget, batch_size)

            # Print statistics
            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('='*70))
            self.stdout.write(self.style.SUCCESS('✓ IMPORT COMPLETED SUCCESSFULLY!'))
            self.stdout.write(self.style.SUCCESS('='*70))
            self.stdout.write(f'Total lines processed: {stats["total_lines"]:,}')
            self.stdout.write(f'Transactions imported: {stats["imported"]:,}')
            self.stdout.write(f'Skipped (errors): {stats["errors"]:,}')
            self.stdout.write(f'Date range: {stats["min_date"]} to {stats["max_date"]}')
            self.stdout.write('')

        except Exception as e:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('='*70))
            self.stdout.write(self.style.ERROR(f'✗ IMPORT FAILED: {str(e)}'))
            self.stdout.write(self.style.ERROR('='*70))
            import traceback
            self.stdout.write(traceback.format_exc())
            raise CommandError(f'Import failed: {e}')

    def parse_and_import(self, csv_file, budget, batch_size):
        """Parse CSV and import in large batches."""
        stats = {
            'total_lines': 0,
            'imported': 0,
            'errors': 0,
            'min_date': None,
            'max_date': None,
        }

        batch = []

        self.stdout.write('Importing transactions...')

        with open(csv_file, 'r', encoding='utf-8', errors='replace') as f:
            # Skip first 2 header lines
            next(f)
            next(f)

            # Read CSV
            reader = csv.DictReader(f, delimiter='^')

            for row in reader:
                stats['total_lines'] += 1

                try:
                    # Parse date - skip if invalid
                    date_str = row.get('Date', '').strip() if row.get('Date') else ''
                    if not date_str or len(date_str) < 8:
                        stats['errors'] += 1
                        continue  # Skip rows without valid dates

                    try:
                        date = datetime.strptime(date_str[:8], '%Y%m%d').date()
                        if stats['min_date'] is None or date < stats['min_date']:
                            stats['min_date'] = date
                        if stats['max_date'] is None or date > stats['max_date']:
                            stats['max_date'] = date
                    except ValueError:
                        stats['errors'] += 1
                        continue  # Skip rows with invalid date format

                    # Parse amount
                    amount_str = row.get('Amount', '0').strip() if row.get('Amount') else '0'
                    try:
                        amount = Decimal(amount_str)
                    except (InvalidOperation, ValueError):
                        amount = Decimal('0')

                    # Create item (truncate long fields to avoid DB errors)
                    description = row.get('Description', '').strip() if row.get('Description') else ''
                    reference_number = row.get('ID', '').strip() if row.get('ID') else ''

                    # Get member, category, source
                    member_name = row.get('Name', '').strip() if row.get('Name') else ''
                    category_name = row.get('Category', '').strip() if row.get('Category') else ''
                    source_name = row.get('Source', '').strip() if row.get('Source') else ''

                    # Get or create related objects
                    member = self.get_or_create_member(member_name) if member_name else None
                    category = self.get_or_create_category(category_name) if category_name else None
                    source = self.get_or_create_source(source_name) if source_name else None

                    # Generate unique_id from reference_number and date
                    unique_id = f"{date.strftime('%Y%m%d')}-{reference_number}" if reference_number else f"{date.strftime('%Y%m%d')}-{stats['imported'] + 1}"

                    item = BudgetItem(
                        budget=budget,
                        date=date,
                        unique_id=unique_id[:100],  # Truncate to 100 chars max
                        description=description[:500] if description else '',  # Truncate to 500 chars
                        monitary_value=amount,
                        reference_number=reference_number[:100] if reference_number else '',  # Truncate to 100 chars
                        sequence_number=stats['imported'] + 1,
                        member=member,
                        source=source
                    )

                    batch.append((item, category))

                    # Bulk create when batch is full
                    if len(batch) >= batch_size:
                        with transaction.atomic():
                            items = [item for item, _ in batch]
                            created_items = BudgetItem.objects.bulk_create(items, ignore_conflicts=True)

                            # Set M2M categories
                            for idx, (item, category) in enumerate(batch):
                                if category and idx < len(created_items):
                                    created_items[idx].categories.add(category)

                        stats['imported'] += len(batch)
                        batch = []
                        self.stdout.write(f'  → {stats["imported"]:,} transactions imported...', ending='\r')
                        self.stdout.flush()

                except Exception as e:
                    stats['errors'] += 1
                    if stats['errors'] <= 5:
                        self.stdout.write(self.style.WARNING(
                            f'\n  ⚠️  Error on line {stats["total_lines"]}: {str(e)}'
                        ))

            # Save remaining batch
            if batch:
                with transaction.atomic():
                    items = [item for item, _ in batch]
                    created_items = BudgetItem.objects.bulk_create(items, ignore_conflicts=True)

                    # Set M2M categories
                    for idx, (item, category) in enumerate(batch):
                        if category and idx < len(created_items):
                            created_items[idx].categories.add(category)

                stats['imported'] += len(batch)

        self.stdout.write('')
        return stats

    def get_or_create_member(self, name):
        """Get or create a Member object."""
        if name not in self.members_cache:
            member, created = Member.objects.get_or_create(name=name)
            self.members_cache[name] = member
        return self.members_cache[name]

    def get_or_create_category(self, name):
        """Get or create a Category object."""
        if name not in self.categories_cache:
            category, created = Category.objects.get_or_create(
                name=name,
                defaults={'description': f'Auto-imported: {name}'}
            )
            self.categories_cache[name] = category
        return self.categories_cache[name]

    def get_or_create_source(self, name):
        """Get or create a Source object."""
        if name not in self.sources_cache:
            source, created = Source.objects.get_or_create(
                name=name,
                defaults={'source_type': 'other'}
            )
            self.sources_cache[name] = source
        return self.sources_cache[name]
