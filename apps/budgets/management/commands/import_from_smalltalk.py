"""
Django management command to import budget data from Smalltalk CSV exports.

Usage:
    python manage.py import_from_smalltalk /path/to/export/directory
"""

import csv
from decimal import Decimal
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from apps.budgets.models import (
    Category, Member, Source, BudgetGroup, Budget, BudgetItem,
    AccountingCategory, CategoryVendor
)


class Command(BaseCommand):
    help = 'Import budget data from Smalltalk CSV exports'

    def add_arguments(self, parser):
        parser.add_argument(
            'export_dir',
            type=str,
            help='Path to directory containing exported CSV files'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before import (DANGEROUS!)',
        )

    def handle(self, *args, **options):
        import_dir = options['export_dir']
        clear_data = options.get('clear', False)

        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('SMALLTALK BUDGET DATA IMPORT'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write('')

        if clear_data:
            self.stdout.write(self.style.WARNING('⚠️  CLEARING ALL EXISTING DATA...'))
            with transaction.atomic():
                BudgetItem.objects.all().delete()
                Budget.objects.all().delete()
                BudgetGroup.objects.all().delete()
                Category.objects.all().delete()
                Member.objects.all().delete()
                Source.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('✓ Data cleared'))
            self.stdout.write('')

        # Track imported objects by their original IDs
        self.category_map = {}
        self.member_map = {}
        self.source_map = {}
        self.group_map = {}
        self.budget_map = {}

        try:
            with transaction.atomic():
                self.import_categories(import_dir)
                self.import_members(import_dir)
                self.import_sources(import_dir)
                self.import_budget_groups(import_dir)
                self.import_budgets(import_dir)
                self.import_transactions(import_dir)

            self.stdout.write('')
            self.stdout.write(self.style.SUCCESS('='*70))
            self.stdout.write(self.style.SUCCESS('✓ IMPORT COMPLETED SUCCESSFULLY!'))
            self.stdout.write(self.style.SUCCESS('='*70))
            self.stdout.write('')

        except Exception as e:
            self.stdout.write('')
            self.stdout.write(self.style.ERROR('='*70))
            self.stdout.write(self.style.ERROR(f'✗ IMPORT FAILED: {str(e)}'))
            self.stdout.write(self.style.ERROR('='*70))
            raise CommandError(f'Import failed: {e}')

    def import_categories(self, import_dir):
        self.stdout.write('Step 1: Importing Categories...')
        file_path = f'{import_dir}/categories.csv'

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                cat = Category.objects.create(
                    name=row['name'],
                    description=row.get('description', '')
                )
                self.category_map[row['id']] = cat
                count += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ Imported {count} categories'))

    def import_members(self, import_dir):
        self.stdout.write('Step 2: Importing Members...')
        file_path = f'{import_dir}/members.csv'

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                member = Member.objects.create(
                    name=row['name'],
                    description=row.get('description', '')
                )
                self.member_map[row['id']] = member
                count += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ Imported {count} members'))

    def import_sources(self, import_dir):
        self.stdout.write('Step 3: Importing Sources...')
        file_path = f'{import_dir}/sources.csv'

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                source = Source.objects.create(
                    name=row['name'],
                    description=row.get('description', ''),
                    account_type=row.get('account_type', '')
                )
                self.source_map[row['id']] = source
                count += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ Imported {count} sources'))

    def import_budget_groups(self, import_dir):
        self.stdout.write('Step 4: Importing Budget Groups...')
        file_path = f'{import_dir}/budget_groups.csv'

        # First pass: create all groups
        groups_data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                groups_data.append(row)
                group = BudgetGroup.objects.create(
                    name=row['name'],
                    description=row.get('description', '')
                )
                self.group_map[row['id']] = group

        # Second pass: set parent relationships
        for row in groups_data:
            if row.get('parent_id'):
                group = self.group_map[row['id']]
                parent = self.group_map.get(row['parent_id'])
                if parent:
                    group.parent = parent
                    group.save()

        self.stdout.write(self.style.SUCCESS(f'  ✓ Imported {len(groups_data)} budget groups'))

    def import_budgets(self, import_dir):
        self.stdout.write('Step 5: Importing Budgets...')
        file_path = f'{import_dir}/budgets.csv'

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                group = self.group_map.get(row['group_id'])
                if not group:
                    self.stdout.write(self.style.WARNING(
                        f"  ⚠️  Skipping budget '{row['name']}' - group not found"
                    ))
                    continue

                budget = Budget.objects.create(
                    name=row['name'],
                    notes=row.get('notes', '').replace(';', ','),  # Restore commas
                    group=group,
                    is_copy=row.get('is_copy', '').lower() == 'true',
                    is_whatif=row.get('is_whatif', '').lower() == 'true'
                )
                self.budget_map[row['id']] = budget
                count += 1

        self.stdout.write(self.style.SUCCESS(f'  ✓ Imported {count} budgets'))

    def import_transactions(self, import_dir):
        self.stdout.write('Step 6: Importing Transactions...')
        self.stdout.write('  (This may take a while for large datasets)')
        file_path = f'{import_dir}/transactions.csv'

        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            skipped = 0
            batch = []
            batch_size = 1000

            for row in reader:
                budget = self.budget_map.get(row['budget_id'])
                if not budget:
                    skipped += 1
                    continue

                # Parse date
                date = None
                if row.get('date'):
                    try:
                        date = datetime.strptime(row['date'], '%Y-%m-%d').date()
                    except ValueError:
                        pass

                # Get related objects
                category = self.category_map.get(row.get('category_name')) if row.get('category_name') else None
                member = self.member_map.get(row.get('member_name')) if row.get('member_name') else None
                source = self.source_map.get(row.get('source_name')) if row.get('source_name') else None

                # Create budget item
                item = BudgetItem(
                    budget=budget,
                    date=date,
                    description=row.get('description', '').replace(';', ','),  # Restore commas
                    monitary_value=Decimal(row.get('amount', '0')),
                    reference_number=row.get('reference_number', ''),
                    sequence_number=int(row.get('sequence_number', '0'))
                )

                batch.append(item)
                count += 1

                # Bulk create in batches
                if len(batch) >= batch_size:
                    BudgetItem.objects.bulk_create(batch)
                    batch = []
                    self.stdout.write(f'    → {count} transactions imported...', ending='\r')

            # Create remaining items
            if batch:
                BudgetItem.objects.bulk_create(batch)

            # Now set M2M relationships
            self.stdout.write('')
            self.stdout.write('  Setting category/member/source relationships...')

            # Re-read file to set relationships
            with open(file_path, 'r', encoding='utf-8') as f2:
                reader2 = csv.DictReader(f2)
                items = BudgetItem.objects.all().order_by('id')

                for idx, row in enumerate(reader2):
                    if idx < len(items):
                        item = items[idx]

                        # Look up by name in the maps
                        if row.get('category_name'):
                            for cat_id, cat in self.category_map.items():
                                if cat.name == row['category_name']:
                                    item.categories.add(cat)
                                    break

                        if row.get('member_name'):
                            for mem_id, mem in self.member_map.items():
                                if mem.name == row['member_name']:
                                    item.members.add(mem)
                                    break

                        if row.get('source_name'):
                            for src_id, src in self.source_map.items():
                                if src.name == row['source_name']:
                                    item.sources.add(src)
                                    break

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'  ✓ Imported {count} transactions'))
        if skipped > 0:
            self.stdout.write(self.style.WARNING(f'  ⚠️  Skipped {skipped} transactions (budget not found)'))
